import RPi.GPIO as GPIO

PIN_DRIVER_IN1 = 22
PIN_DRIVER_IN2 = 24

# Define PIN output Servo
PIN_SERVO_EGG_SPAR = 12
PIN_SERVO_EMITTER = 11


# Define PIN input IR Sensor
PIN_IR_SENSOR = 16

GPIO.setmode(GPIO.BOARD)
GPIO.setup(PIN_IR_SENSOR,GPIO.OUT) # ir sensor set input
GPIO.setup(PIN_SERVO_EGG_SPAR, GPIO.OUT) # egg spar set output
GPIO.setup(PIN_SERVO_EMITTER, GPIO.OUT) # emiter set output
GPIO.setup(PIN_DRIVER_IN1,GPIO.OUT) # driver set output
GPIO.setup(PIN_DRIVER_IN2,GPIO.OUT) # driver set output

GPIO.output(PIN_DRIVER_IN1,GPIO.LOW) # driver set to low/off
GPIO.output(PIN_DRIVER_IN2,GPIO.LOW) # driver

GPIO.setup(PIN_IR_SENSOR,GPIO.LOW) # ir sensor set input
print('Set Default state')
GPIO.cleanup()