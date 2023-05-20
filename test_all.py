import smbus
from time import sleep
import RPi.GPIO as GPIO

GPIO.setwarnings(False)
PIN_SERVO_EGG_SPAR = 12
PIN_SERVO_EMITTER = 11

GPIO.setmode(GPIO.BOARD)
GPIO.setmode(GPIO.BCM)
GPIO.setup(PIN_SERVO_EGG_SPAR, GPIO.OUT)
GPIO.setup(PIN_SERVO_EMITTER, GPIO.OUT)


pwm_egg_spar = GPIO.PWM(PIN_SERVO_EGG_SPAR, 50)
pwm_egg_spar.start(0)

pwm_emitter = GPIO.PWM(PIN_SERVO_EMITTER, 50)
pwm_emitter.start(0)

def setAngle(angle):
    duty = angle / 18 + 2
    GPIO.output(PIN_SERVO_EGG_SPAR, True)
    pwm_egg_spar.ChangeDutyCycle(duty)
    sleep(1)
    GPIO.output(PIN_SERVO_EGG_SPAR, False)
    pwm_egg_spar.ChangeDutyCycle(duty)

def setAngleEmitter(angle):
    duty = angle / 18 + 2
    GPIO.output(PIN_SERVO_EMITTER, True)
    pwm_emitter.ChangeDutyCycle(duty)
    sleep(1)
    GPIO.output(PIN_SERVO_EMITTER, False)
    pwm_emitter.ChangeDutyCycle(duty)

count = 0
numLoops = 1

print('SEVO TEST')
while count < numLoops:
    print("set to 0-deg")
    setAngle(0)
    sleep(1)

        
    print("set to 90-deg")
    setAngle(90)
    sleep(1)

    print("set to 135-deg")
    setAngle(135)
    sleep(1)


    print("set to 0-deg")
    setAngleEmitter(0)
    sleep(1)

        
    print("set to 90-deg")
    setAngleEmitter(90)
    sleep(1)

    print("set to 135-deg")
    setAngleEmitter(135)
    sleep(1)
    
    count=count+1

pwm_egg_spar.stop()
pwm_emitter.stop()

import time

INPUT_IR = 16

GPIO.setup(INPUT_IR,GPIO.IN)

print('IR SENSOR TEST')
for i in range(10):
    if GPIO.input(INPUT_IR):
        print("object detected")
    time.sleep(1)


print('BHxxx SENSOR TEST')
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
 
for i in range(10):
    print("Light Level : " + str(readLight()) + " lux")
    time.sleep(0.5)



print('TEST DRIVER')
in1 = 24
in2 = 23
en = 25
temp1 = 1

GPIO.setup(in1,GPIO.OUT)
GPIO.setup(in2,GPIO.OUT)
GPIO.setup(en,GPIO.OUT)

GPIO.output(in1,GPIO.LOW)
GPIO.output(in2,GPIO.LOW)

p=GPIO.PWM(en,1000)

while True:
    print('start')
    GPIO.output(in1,GPIO.HIGH)
    GPIO.output(in2,GPIO.LOW)
    p.ChangeDutyCycle(25)
    sleep(0.1)

GPIO.cleanup()