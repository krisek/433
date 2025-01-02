# 433MHz Signal Recorder and Replayer

This repository contains a framework to record and replay 433MHz signals using a Raspberry Pi. It includes scripts for recording signals, replaying them, and an API server to facilitate the integraton replaying signals.

The inspiration for this project came from https://carson.fenimorefamily.com/?p=471, the rpi-rfsniffer referred there is not relevant anymore as GPIO access has slightly changed on Raspbian. 

## API server

The API is only a reference implementation to replicate the functionality of a AC-123-06D remote controlling my blinds/shutters, but it can be easily adopted to control any other devices.

## Installation Instructions

1. **Clone the repository:**
   ```bash
   git clone https://github.com/krisek/433
   cd 433
   ```

2. **Install the required libraries:**
   ```bash
   sudo apt install python3-fastapi python3-mathplotlib python3-rpi-lgpio
   ```

3. **Set up the GPIO:**
   Ensure you have the necessary hardware setup to connect the 433MHz transmitter and receiver to the Raspberry Pi.

## Usage

### Recording Signals

To record signals, run the `record.py` script:
```bash
python record.py --gpio <GPIO_PIN> --filename <FILENAME>
```
- `--gpio`: GPIO pin number to read the signal from (default: 17).
- `--filename`: File to save the pulse data and visualization (default: timestamped).

You can record multiple signals in one recording session as the replay script supports replaying only a spefic chunk of the recording.

The recorder generates two files, one text file that contains the raw gpio transitions and a png that shows the signal. I added the signals I recorded from my remote controller, it is quite obvious where are the real emitted signals and where is only noise.

### Replaying Signals

To replay signals, run the `replay.py` script:
```bash
python replay.py --gpio <GPIO_PIN> --filename <FILENAME> --start-at <START_TIME> --stop-at <STOP_TIME>
```
- `--gpio`: GPIO pin number for the transmitter.
- `--filename`: Filename containing the recorded signal data.
- `--start-at`: Time in milliseconds to start replaying the signal (default: 0).
- `--stop-at`: Time in milliseconds to stop replaying the signal (default: end of the file).

In the scripts directory there are shell scripts that can be used to emit signals. But a much civilized way is to do this over the API server, you just need to create a blinds.yaml file (as per example in the repository) and you can either integrate the API server into Home Assistant or use the provided frontend to emit signals.

### API Server

To start the API server, run the `api.py` script:
```bash
python api.py --port <PORT> --gpio <GPIO_PIN>
```
- `--port`: Port for the API server (default: 8000).
- `--gpio`: GPIO pin number for the transmitter (default: 27).

The API server provides the following endpoints:
- `GET /`: Serve the static index.html file.
- `GET /blinds`: Get metadata of blinds from `blinds.yaml`.
- `POST /replay_signal`: Replay a recorded signal for a specific blind.
- `POST /login` or `GET /login`: Get an access token
- all other requests will be tried to be served from the static sub-direcotry

Once you started the api server, just point your browser to http://ip-of-your-rpi:8080 and the fronted will be served.

## Files Description

- **record.py**: Script to record 433MHz signals and save the pulse data and visualization.
- **replay.py**: Script to replay recorded 433MHz signals.
- **api.py**: API server to control blinds using the recorded signals.
- **blinds.yaml**: Configuration file for blinds, specifying the actions and corresponding signal files.
- **data** / **scripts** sub-directories: recordings and replay scripts from/for my AC-123-06D remote

## Contributing

Contributions are welcome! Please fork the repository and submit a pull request.

## License

This project is licensed under the MIT License.
