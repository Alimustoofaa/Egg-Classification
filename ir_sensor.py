import RPi.GPIO as GPIO
import time

INPUT_IR = 16

GPIO.setmode(GPIO.BOARD)
GPIO.setup(INPUT_IR,GPIO.IN)

try:
    while True:
        if GPIO.input(INPUT_IR):
            print("object detected")
        time.sleep(1)
except KeyboardInterrupt:
    GPIO.cleanup()
