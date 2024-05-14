#!/usr/bin/python3

# Tested on Raspberry Pi OS. Requirements: enable SPI, for example
# from raspi-config. The example is based on a SparkFun tutorial:
# https://learn.sparkfun.com/tutorials/python-programming-tutorial-getting-started-with-the-raspberry-pi/experiment-3-spi-and-analog-input

import signal
import sys
import time
import datetime
import spidev
import RPi.GPIO as GPIO
import json
import os



spi_ch = 0

# Enable SPI
spi = spidev.SpiDev(0, spi_ch)
spi.max_speed_hz = 1200000

def close(signal, frame):
    sys.exit(0)

signal.signal(signal.SIGINT, close)

def get_adc(channel):

    # Make sure ADC channel is 0 or 1
    if channel != 0:
        channel = 1

    # Construct SPI message
    #  First bit (Start): Logic high (1)
    #  Second bit (SGL/DIFF): 1 to select single mode
    #  Third bit (ODD/SIGN): Select channel (0 or 1)
    #  Fourth bit (MSFB): 0 for LSB first
    #  Next 12 bits: 0 (don't care)
    msg = 0b11
    msg = ((msg << 1) + channel) << 5
    msg = [msg, 0b00000000]
    reply = spi.xfer2(msg)

    # Construct single integer out of the reply (2 bytes)
    adc = 0
    for n in reply:
        adc = (adc << 8) + n

    # Last bit (0) is not part of ADC value, shift to remove it
    adc = adc >> 1
    
    # Calculate voltage form ADC value
    # considering the soil moisture sensor is working at 5V
    # print("adc directo "+str(adc)+" "+str((5 * adc) / 1023))
    # voltage = (5 * adc) / 1023

    return adc

def get_temp(channel):
    if channel != 0:
        channel = 1
    # Construct SPI message
    #  First bit (Start): Logic high (1)
    #  Second bit (SGL/DIFF): 1 to select single mode
    #  Third bit (ODD/SIGN): Select channel (0 or 1)
    #  Fourth bit (MSFB): 0 for LSB first
    #  Next 12 bits: 0 (don't care)
    msg = 0b11
    msg = ((msg << 1) + channel) << 5
    msg = [msg, 0b00000000]
    reply = spi.xfer2(msg)

    # Construct single integer out of the reply (2 bytes)
    adc = 0
    for n in reply:
        adc = (adc << 8) + n

    # Last bit (0) is not part of ADC value, shift to remove it
    adc = adc >> 1

    # Calculate voltage form ADC value
    # considering the soil moisture sensor is working at 5V

    return ((adc*5/1023)-(1.51))*17/1.01

def adcAvr(channel):
    #Channel 0 Temperature
    #Channel 1 Luminocity
    avr=0

    if channel != 0:
        for i in range(10):
            avr+=get_adc(1)
            time.sleep(0.2)
    else:
        for i in range(10):
            avr+=get_temp(0)
            time.sleep(0.2)


    return round(avr/10)


def getValues():
    dt=datetime.datetime.now()
    datos = {
    "timestamp":dt,
    "temperature": adcAvr(0),
    "luminocity":adcAvr(1)
    # "luminosidad": luminosidad
    }
    return datos
    ruta_archivo = '/home/pi/Desktop/test.json'
    with open(ruta_archivo, 'w') as archivo_json:
        json.dump(datos, archivo_json)
    try:
        with open(ruta_archivo, 'w') as archivo_json:
            json.dump(datos, archivo_json)
    except Exception as e:
        print(f"¡Error! No se pudo crear el archivo JSON: {e}")


#Function for testing porpouses
def printValues():
    while True:
       
        print("Luminocity "+str(adcAvr(1)))
        print("Time stamp "+str(time.time()))
        print("Temperature "+str(adcAvr(0)))
        print("------------------")
        time.sleep(2)