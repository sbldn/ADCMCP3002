import ADCMCP3002
import signal
import json
import time


def signal_handler(sig, frame):
    sensor.close()

sensor=ADCMCP3002.SensorReader()
signal.signal(signal.SIGINT, signal_handler)

if __name__ == "__main__":
    try:
        while True:
            data = sensor.get_values()
            print(json.dumps(data, indent=4))
            time.sleep(1)  # Ajusta según sea necesario
    except KeyboardInterrupt:
        sensor.close()