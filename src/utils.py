import time
import RPi.GPIO as GPIO

# function angle servo
def set_angle_servo(angle, pin, pwm):
    duty = angle / 18 + 2
    GPIO.output(pin, True)
    pwm.ChangeDutyCycle(duty)
    

def reset_angel_servo(angle, pin, pwm):
    duty = angle / 18 + 2
    GPIO.output(pin, False)
    pwm.ChangeDutyCycle(duty)

# function bh sensor
def convert_to_number(data):
    # Simple function to convert 2 bytes of data
    # into a decimal number
    return int(((data[1] + (256 * data[0])) / 1.2))