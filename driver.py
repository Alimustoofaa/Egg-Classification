import RPi.GPIO as GPIO
from time import sleep

# in1 = 29
# in2 = 31
# en = 22

in1 = 22
in2 = 24
en = 18
temp1 = 1

GPIO.setmode(GPIO.BOARD)
GPIO.setup(in1,GPIO.OUT)
GPIO.setup(in2,GPIO.OUT)
GPIO.setup(en,GPIO.OUT)
GPIO.output(in1,GPIO.LOW)
GPIO.output(in2,GPIO.LOW)
# p=GPIO.PWM(en,1000)
# p.start(25)

try:
    while True:
        print('Driver STOP')
        GPIO.output(in1,GPIO.LOW)
        GPIO.output(in2,GPIO.LOW)
except KeyboardInterrupt:
    pass

try:
    while True:
        print('start')
        GPIO.output(in1,GPIO.HIGH)
        GPIO.output(in2,GPIO.LOW)
        sleep(0.1)
except KeyboardInterrupt:
    GPIO.cleanup()