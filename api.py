from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.responses import JSONResponse, FileResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
import RPi.GPIO as GPIO
import time
import argparse
import os
import logging
import yaml

app = FastAPI()

# Static token for simplicity
STATIC_TOKEN = os.environ.get('ACCESS_TOKEN', 'mysecrettoken')
gpio_pin = 27

parser = argparse.ArgumentParser(description="Blinds control server")
parser.add_argument("--port", "-p", default=8000, type=int, help="Port for the API server")
parser.add_argument("--gpio", default=27, type=int, help="GPIO pin number for the transmitter.")
args = parser.parse_args()
gpio_pin = args.gpio
# GPIO Setup

GPIO.setmode(GPIO.BCM)
GPIO.setup(gpio_pin, GPIO.OUT)

# Logger configuration
logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.WARNING)
logger = logging.getLogger(__name__)

# Load blinds configuration
def load_blinds_config(file_path="blinds.yaml"):
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"{file_path} not found.")
    with open(file_path, "r") as file:
        return yaml.safe_load(file)

try:
    blinds_config = load_blinds_config()
    logger.info("Blinds configuration loaded successfully.")
except FileNotFoundError as e:
    logger.error(e)
    blinds_config = {}

def verify_token(request: Request):
    auth_header = request.headers.get('Authorization')
    token = None
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header[len("Bearer "):]
    if not token:
        token = request.query_params.get('token')
    if not token or token != STATIC_TOKEN:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return token

@app.get("/")
def read_root():
    return FileResponse("static/index.html")

@app.get("/blinds")
def get_blinds_metadata(token: str = Depends(verify_token)):
    """
    Serve metadata of blinds from blinds.yaml.
    """
    return blinds_config

@app.post("/replay_signal")
def replay_signal(
    blind_name: str,
    action: str,
    token: str = Depends(verify_token)
):
    """
    Replay a recorded signal for a specific blind.
    :param blind_name: The name of the blind as per the blinds.yaml configuration.
    :param action: up/down/stop
    """
    filename = ""

    for blind in blinds_config['blinds']:
        if blind_name == blind['name']:
            print(blind)
            start_at = blind['actions'][action].get("start", 0),
            stop_at = blind['actions'][action].get("stop", None),
            filename = blind['actions'][action]['filename']
            break

            
    if filename == "":
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Blind not found in configuration.")

    if not gpio_pin or not filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid configuration for blind {blind_name}: Missing gpio_pin or signal_file."
        )


    logger.info(f"Transmitting signal for {blind_name} from {filename} on GPIO {gpio_pin} / {start_at} / {stop_at}")
    print(f"Transmitting signal for {blind_name} from {filename} on GPIO {gpio_pin} / {start_at[0]} / {stop_at[0]}")
    for i in range(3):
        try:
            with open(filename, "r") as file:
                signal_data = [line.strip().split(",") for line in file]
                signal_data = [(float(high), float(low)) for high, low in signal_data]

            cumulative_time = 0
            filtered_signal = []
            for high_duration, low_duration in signal_data:
                next_cumulative_time = cumulative_time + (high_duration + low_duration) * 1000  # Convert to ms
                if next_cumulative_time >= start_at[0]:
                    filtered_signal.append((high_duration, low_duration))
                if stop_at is not None and next_cumulative_time >= stop_at[0]:
                    break
                cumulative_time = next_cumulative_time

            for high_duration, low_duration in filtered_signal:
                GPIO.output(gpio_pin, GPIO.HIGH)
                time.sleep(high_duration)
                GPIO.output(gpio_pin, GPIO.LOW)
                time.sleep(low_duration)

            return {"message": f"Signal transmission for {blind_name} completed."}

        except FileNotFoundError:
            logger.error(f"File {filename} not found.")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Signal file not found")
        except Exception as e:
            logger.error(f"An error occurred: {e}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
        time.sleep(0.5)
#    finally:
#        GPIO.cleanup()
#        logger.info("GPIO cleanup completed.")

@app.post("/login")
@app.get("/login")
def login():
    return {"access_token": STATIC_TOKEN}


# Mount static files for the frontend
app.mount("/", StaticFiles(directory="static", html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=args.port)
