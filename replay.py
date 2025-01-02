import RPi.GPIO as GPIO
import time
import argparse


def replay_signal(gpio_pin, filename, start_at=0, stop_at=None):
    """
    Replay a recorded signal on a transmitter.
    :param gpio_pin: GPIO pin number to which the transmitter is connected.
    :param filename: Path to the file containing the recorded signal data.
    :param start_at: Time in milliseconds to start replaying the signal.
    :param stop_at: Time in milliseconds to stop replaying the signal.
    """
    # Setup GPIO
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(gpio_pin, GPIO.OUT)
    print(f"Transmitting signal from {filename} on GPIO {gpio_pin}")

    try:
        # Load signal data from file
        with open(filename, "r") as file:
            signal_data = [line.strip().split(",") for line in file]
            signal_data = [(float(high), float(low)) for high, low in signal_data]

        # Calculate cumulative durations to determine playback range
        cumulative_time = 0
        filtered_signal = []
        for high_duration, low_duration in signal_data:
            next_cumulative_time = cumulative_time + (high_duration + low_duration) * 1000  # Convert to ms
            if next_cumulative_time >= start_at:
                filtered_signal.append((high_duration, low_duration))
            if stop_at is not None and next_cumulative_time >= stop_at:
                break
            cumulative_time = next_cumulative_time

        # Transmit the filtered signal
        for high_duration, low_duration in filtered_signal:
            # Set HIGH signal
            GPIO.output(gpio_pin, GPIO.HIGH)
            time.sleep(high_duration)

            # Set LOW signal
            GPIO.output(gpio_pin, GPIO.LOW)
            time.sleep(low_duration)

        print("Signal transmission completed.")

    except FileNotFoundError:
        print(f"Error: File {filename} not found.")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        GPIO.cleanup()
        print("GPIO cleanup completed.")


if __name__ == "__main__":
    # Command-line argument parsing
    parser = argparse.ArgumentParser(description="Replay a recorded signal on a transmitter.")
    parser.add_argument("--gpio", type=int, help="GPIO pin number for the transmitter.")
    parser.add_argument("--filename", type=str, help="Filename containing the recorded signal data.")
    parser.add_argument("--start-at", type=int, default=0, help="Start replay from this time (in ms).")
    parser.add_argument("--stop-at", type=int, default=None, help="Stop replay at this time (in ms).")
    args = parser.parse_args()

    # Call the replay function
    replay_signal(args.gpio, args.filename, start_at=args.start_at, stop_at=args.stop_at)
