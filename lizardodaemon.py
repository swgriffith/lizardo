#!/usr/bin/env python3
from Adafruit_GPIO import I2C
import logging
import time
import smbus
from prometheus_client import Gauge, start_http_server
from systemd.journal import JournalHandler

# Setup logging to the Systemd Journal
log = logging.getLogger('sht30_sensor')
log.addHandler(JournalHandler())
log.setLevel(logging.INFO)

# The time in seconds between sensor reads
READ_INTERVAL = 5.0

# Create Prometheus gauges for humidity and temperature in
# Celsius and Fahrenheit
# Sensor 1 - Multiplexer Channel 0
gh = Gauge('sht30_humidity_percent','Humidity percentage measured by the SHT30 Sensors', ['scale'])
gt = Gauge('sht30_temperature','Temperature measured by the SHT30 Sensors', ['scale'])

# Initialize the labels for the temperature scale
gh.labels('sensor0_humidity')
gt.labels('sensor0_fahrenheit')
gh.labels('sensor1_humidity')
gt.labels('sensor1_fahrenheit')

tca = I2C.get_i2c_device(address=0x70)

def tca_select(channel):
    """Select an individual channel."""
    if channel > 7:
        return
    tca.writeRaw8(1 << channel)

def read_sensors(channel):
    try:
        # Initialize the SHT30 sensor
        # Select channel 0
        tca_select(channel)
        # Get I2C bus
        bus = smbus.SMBus(1)
        # SHT30 address, 0x44(68)
        # Send measurement command, 0x2C(44)
        # 0x06(06)        High repeatability measurement
        bus.write_i2c_block_data(0x44, 0x2C, [0x06])
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
        gh.labels("sensor{0}_humidity".format(channel)).set(humidity)
        gt.labels("sensor{0}_fahrenheit".format(channel)).set(fTemp)

        log.info("Sensor {0} - Temp:{1:0.1f}*F, Humidity: {2:0.1f}%".format(channel, fTemp, humidity))

if __name__ == "__main__":
    # Expose metrics
    metrics_port = 8000
    start_http_server(metrics_port)
    print("Serving sensor metrics on :{}".format(metrics_port))
    log.info("Serving sensor metrics on :{}".format(metrics_port))

    while True:
        read_sensors(0)
        read_sensors(1)
