import smbus
import time
from flask import Flask

app = Flask(__name__)

@app.route('/')
def index():
	# Get I2C bus
	bus = smbus.SMBus(1)
	# SHT30 address, 0x44(68)
	# Send measurement command, 0x2C(44)
	#               0x06(06)        High repeatability measurement
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
	return "<html><head><title>Tank Weather</title></head><body><h1>Lucy and Caela!!!</h1><h1>Tank Weather</h1><p>Relative Humidity : {:.2f}%</p><p>Temp : {:.2f}°</b></body></html>".format(humidity,fTemp)

if __name__ == '__main__':
	app.debug = True
	app.run(host="0.0.0.0")
