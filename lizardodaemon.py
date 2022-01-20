#!/usr/bin/env python3

import logging
import time

import smbus

from prometheus_client import Gauge, start_http_server
from systemd.journal import JournalHandler

# Setup logging to the Systemd Journal
log = logging.getLogger('sht30_sensor')
log.addHandler(JournalHandler())
log.setLevel(logging.INFO)

# Initialize the SHT30 sensor
# Get I2C bus
bus = smbus.SMBus(1)
# SHT30 address, 0x44(68)
# Send measurement command, 0x2C(44)
#               0x06(06)        High repeatability measurement
bus.write_i2c_block_data(0x44, 0x2C, [0x06])

# The time in seconds between sensor reads
READ_INTERVAL = 30.0

# Create Prometheus gauges for humidity and temperature in
# Celsius and Fahrenheit
gh = Gauge('sht30_humidity_percent','Humidity percentage measured by the SHT30 Sensor')
gt = Gauge('sht30_temperature','Temperature measured by the SHT30 Sensor', ['scale'])

# Initialize the labels for the temperature scale
gt.labels('celsius')
gt.labels('fahrenheit')


def read_sensor():
    try:
        # SHT30 address, 0x44(68)
        # Read data back from 0x00(00), 6 bytes
        # cTemp MSB, cTemp LSB, cTemp CRC, Humididty MSB, Humidity LSB, Humidity CRC
        data = bus.read_i2c_block_data(0x44, 0x00, 6)
        # Convert the data
        cTemp = ((((data[0] * 256.0) + data[1]) * 175) / 65535.0) - 45
        fTemp = cTemp * 1.8 + 32
        humidity = 100 * (data[3] * 256 + data[4]) / 65535.0
    except RuntimeError as e:
        # GPIO access may require sudo permissions
        # Other RuntimeError exceptions may occur, but
        # are common.  Just try again.
        log.error("RuntimeError: {}".format(e))

    if humidity is not None and cTemp is not None and fTemp is not None:
        gh.set(humidity)
        gt.labels('celsius').set(cTemp)
        gt.labels('fahrenheit').set(fTemp)

        log.info("Temp:{0:0.1f}*C, Temp:{0:0.1f}*F, Humidity: {1:0.1f}%".format(cTemp, fTemp, humidity))

    time.sleep(READ_INTERVAL)

if __name__ == "__main__":
    # Expose metrics
    metrics_port = 8000
    start_http_server(metrics_port)
    print("Serving sensor metrics on :{}".format(metrics_port))
    log.info("Serving sensor metrics on :{}".format(metrics_port))

    while True:
        read_sensor()
