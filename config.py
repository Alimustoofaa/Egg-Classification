import platform
import os

ROOT = os.path.normpath(os.path.dirname(__file__))
PORT = 8000

# Define PIN driver
PIN_DRIVER_IN1 = 24
PIN_DRIVER_IN2 = 23

# Define PIN output Servo
PIN_SERVO_EGG_SPAR = 12
PIN_SERVO_EMITTER = 11


# Define PIN input IR Sensor
PIN_IR_SENSOR = 16

# Define some constants from the datasheet
DEVICE     = 0x23 # Default device I2C address
POWER_DOWN = 0x00 # No active state
POWER_ON   = 0x01 # Power on
RESET      = 0x07 # Reset data register value
ONE_TIME_HIGH_RES_MODE = 0x20

# Define condition lux light
LUX_MIN = 500
LUX_MAX = 2000


# Define delay time object detection
DELAY_OBJECT_DETECTION = 3