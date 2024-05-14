#!/usr/bin/python3

# Tested on Raspberry Pi OS. Requirements: enable SPI, for example
# from raspi-config. The example is based on a SparkFun tutorial:
# https://learn.sparkfun.com/tutorials/python-programming-tutorial-getting-started-with-the-raspberry-pi/experiment-3-spi-and-analog-input

#!/usr/bin/python3

import sys
import datetime
import spidev

class SensorReader:
    def __init__(self, spi_channel=0):
        self.spi = spidev.SpiDev()
        self.spi.open(0, spi_channel)
        self.spi.max_speed_hz = 1200000

    def close(self):
        self.spi.close()
        sys.exit(0)

    def read_adc(self, channel):
        if channel != 0:
            channel = 1
        msg = 0b11
        msg = ((msg << 1) + channel) << 5
        msg = [msg, 0b00000000]
        reply = self.spi.xfer2(msg)
        adc = 0
        for n in reply:
            adc = (adc << 8) + n
        adc = adc >> 1
        return adc

    def read_temperature(self):
        adc = self.read_adc(0)
        voltage = (adc * 5) / 1023
        temperature = ((voltage * 5 / 1023) - 1.51) * 17 / 1.01
        return temperature

    def read_luminosity(self):
        adc = self.read_adc(1)
        return adc

    def read_average_adc(self, channel, samples=10):
        total = sum(self.read_adc(channel) for _ in range(samples))
        return total / samples

    def get_values(self):
        timestamp = datetime.datetime.now()
        temperature = self.read_average_adc(0)
        luminosity = self.read_average_adc(1)
        return {
            "Date": timestamp.strftime("%Y-%m-%d %H:%M:%S"),
            "Temperature": temperature,
            "Light": luminosity
        }