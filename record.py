import RPi.GPIO as GPIO
import time
import matplotlib.pyplot as plt
from datetime import datetime
import argparse

# Generate a timestamp for default file names
default_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

# Configure argument parser
parser = argparse.ArgumentParser(description="Signal Recorder")
parser.add_argument("--gpio", type=int, default=17, help="GPIO number to read signal from (default: 17)")
parser.add_argument("--filename", type=str, default=f"signal_data_{default_timestamp}", help="File to save the pulse data and visualization (default: timestamped)")
args = parser.parse_args()

gpio_pin = args.gpio
filename = args.filename

# Configure GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(gpio_pin, GPIO.IN)

# Main function to capture pulses and visualize them
def main():
    pulse_data = []
    start_time = None
    MIN_DURATION = 0  # Minimum duration to filter out spikes
    print("Recording pulses. Press Ctrl+C to stop.")

    try:
        while True:
            # Wait for a HIGH signal
            while GPIO.input(gpio_pin) == GPIO.LOW:
                pass
            start_time = time.time()

            # Wait for a LOW signal and record the duration
            while GPIO.input(gpio_pin) == GPIO.HIGH:
                pass
            high_duration = time.time() - start_time

            # Wait for the next HIGH signal and record the LOW duration
            start_time = time.time()
            while GPIO.input(gpio_pin) == GPIO.LOW:
                pass
            low_duration = time.time() - start_time

            # Filter out spikes
            if high_duration >= MIN_DURATION and low_duration >= MIN_DURATION:
                pulse_data.append((high_duration, low_duration))

    except KeyboardInterrupt:
        print("\nRecording stopped.")

    finally:
        GPIO.cleanup()

        # Save the captured data to a file
        with open(filename + '.txt', "w") as file:
            for high, low in pulse_data:
                file.write(f"{high:.6f},{low:.6f}\n")
        print(f"Pulse data saved to {filename}.txt")

        # Visualize the captured data
        visualize_data(pulse_data, scale_factor=10000000)

def visualize_data(pulse_data, scale_factor=1000):
    """
    Visualize the pulse data using Matplotlib with explicit time axis scaling.
    :param pulse_data: List of (high_duration, low_duration) tuples.
    :param scale_factor: Factor to scale durations (e.g., 1000 for milliseconds).
    """
    # Scale durations for better visualization
    scaled_pulse_data = [(high * scale_factor, low * scale_factor) for high, low in pulse_data]

    # Create a time axis and signal representation
    time_axis = []
    signal = []
    current_time = 0.0

    for high, low in scaled_pulse_data:
        time_axis.append(current_time)
        signal.append(1)  # High signal
        current_time += high
        time_axis.append(current_time)
        signal.append(0)  # Low signal
        current_time += low

    # Explicitly set the x-axis range to match the total duration
    total_duration = current_time  # Final time from the loop

    # Plot the recorded signal
    plt.figure(figsize=(160, 6))  # Increase figure width for more detail
    plt.step(time_axis, signal, where="post", label="Signal")
    plt.xlabel(f"Time ({'ms' if scale_factor == 1000 else 's'})")
    plt.ylabel("Signal Level")
    plt.title("433 MHz Signal Visualization")
    plt.ylim(-0.5, 1.5)  # Keep signal range between 0 and 1
    plt.xlim(0, total_duration)  # Set x-axis range explicitly
    plt.grid(True)
    plt.legend()

    # Save the plot with a timestamped filename
    plot_filename = f"{filename}.png"
    plt.savefig(plot_filename)
    print(f"Signal visualization saved as {plot_filename}")
    plt.show()

if __name__ == "__main__":
    main()
