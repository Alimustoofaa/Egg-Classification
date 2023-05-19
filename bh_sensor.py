# import time
# import board
# import adafruit_bh1750

# # i2c = board.I2C()  # uses board.SCL and board.SDA
# #sensor = adafruit_bh1750.BH1750()

# while True:
#     lux_value = int(sensor.lux)
#     # if lux_value in range(500, 1001):
#     print('Capture Image', lux_value)
#     # print("%.2f Lux" % sensor.lux)
#     time.sleep(1)


import smbus
import time
 
# Define some constants from the datasheet
DEVICE     = 0x23 # Default device I2C address
POWER_DOWN = 0x00 # No active state
POWER_ON   = 0x01 # Power on
RESET      = 0x07 # Reset data register value
ONE_TIME_HIGH_RES_MODE = 0x20

bus = smbus.SMBus(1)  # Rev 2 Pi uses 1
 
def convertToNumber(data):
  # Simple function to convert 2 bytes of data
  # into a decimal number
  return ((data[1] + (256 * data[0])) / 1.2)
 
def readLight(addr=DEVICE):
  data = bus.read_i2c_block_data(addr,ONE_TIME_HIGH_RES_MODE)
  return convertToNumber(data)
 
while True:
    print("Light Level : " + str(readLight()) + " lux")
    time.sleep(0.5)


