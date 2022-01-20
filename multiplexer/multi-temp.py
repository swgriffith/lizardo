from Adafruit_GPIO import I2C
import smbus
import time

tca = I2C.get_i2c_device(address=0x70)

def tca_select(channel):
    """Select an individual channel."""
    if channel > 7:
        return
    tca.writeRaw8(1 << channel)

def tca_set(mask):
    """Select one or more channels.
           chan =   76543210
           mask = 0b00000000
    """
    if mask > 0xff:
        return
    tca.writeRaw8(mask)

# Select channel 0
tca_select(0)
# you're now talking to OLED on channel 0
# SHT30 address, 0x44(68)
# Send measurement command, 0x2C(44)
#               0x06(06)        High repeatability measurement
bus = smbus.SMBus(1)
bus.write_i2c_block_data(0x44, 0x2C, [0x06])
time.sleep(0.5)
# SHT30 address, 0x44(68)
# Read data back from 0x00(00), 6 bytes
# cTemp MSB, cTemp LSB, cTemp CRC, Humididty MSB, Humidity LSB, Humidity CRC
data = bus.read_i2c_block_data(0x44, 0x00, 6)
# Convert the data
cTemp = ((((data[0] * 256.0) + data[1]) * 175) / 65535.0) - 45
fTemp = cTemp * 1.8 + 32
humidity = 100 * (data[3] * 256 + data[4]) / 65535.0

print("Temp:{0:0.1f}*C, Temp:{1:0.1f}*F, Humidity: {2:0.1f}%".format(cTemp, fTemp, humidity))
# Select channel 1
tca_select(1)
# you're now talking to OLED on channel 1
# you're now talking to OLED on channel 0
# SHT30 address, 0x44(68)
# Send measurement command, 0x2C(44)
#               0x06(06)        High repeatability measurement
bus = smbus.SMBus(1)
bus.write_i2c_block_data(0x44, 0x2C, [0x06])
time.sleep(0.5)
# SHT30 address, 0x44(68)
# Read data back from 0x00(00), 6 bytes
# cTemp MSB, cTemp LSB, cTemp CRC, Humididty MSB, Humidity LSB, Humidity CRC
data = bus.read_i2c_block_data(0x44, 0x00, 6)
# Convert the data
cTemp = ((((data[0] * 256.0) + data[1]) * 175) / 65535.0) - 45
fTemp = cTemp * 1.8 + 32
humidity = 100 * (data[3] * 256 + data[4]) / 65535.0

print("Temp:{0:0.1f}*C, Temp:{1:0.1f}*F, Humidity: {2:0.1f}%".format(cTemp, fTemp, humidity))
#
# etc
#

# Select channels 2 and 0
tca_set(0b0000101)
# you're now talking to OLED on channels 0 and 2 simultaneously
