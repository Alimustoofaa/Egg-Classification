import cv2
import time
import smbus
import RPi.GPIO as GPIO
from picamera import PiCamera
from picamera.array import PiRGBArray

from .utils import convert_to_number,\
				set_angle_servo, reset_angel_servo

from config import DEVICE, RESET,\
				POWER_DOWN, POWER_ON,\
				PIN_DRIVER_IN1, PIN_DRIVER_IN2,\
				ONE_TIME_HIGH_RES_MODE,\
				LUX_MIN, LUX_MAX, \
				PIN_IR_SENSOR, \
				DELAY_OBJECT_DETECTION,\
				PIN_SERVO_EGG_SPAR, PIN_SERVO_EMITTER

print('Setup Sensor')
# declaring Rev 2 Pi uses 1
BUS = smbus.SMBus(1)

# declaring hidden warnings
GPIO.setwarnings(False)

# declaring the BCM mode of pins
GPIO.setmode(GPIO.BOARD)

# set behaviour of sensors
GPIO.setup(PIN_IR_SENSOR,GPIO.IN) # ir sensor set input
GPIO.setup(PIN_SERVO_EGG_SPAR, GPIO.OUT) # egg spar set output
GPIO.setup(PIN_SERVO_EMITTER, GPIO.OUT) # emiter set output
GPIO.setup(PIN_DRIVER_IN1,GPIO.OUT) # driver set output
GPIO.setup(PIN_DRIVER_IN2,GPIO.OUT) # driver set output

GPIO.output(PIN_DRIVER_IN1,GPIO.LOW) # driver set to low/off
GPIO.output(PIN_DRIVER_IN2,GPIO.LOW) # driver set to low/off

# create pwm object
pwm_egg_spar = GPIO.PWM(PIN_SERVO_EGG_SPAR, 50)
pwm_egg_spar.start(0)

pwm_emitter = GPIO.PWM(PIN_SERVO_EMITTER, 50)
pwm_emitter.start(0)


# initialize the camera
camera = PiCamera()
camera.resolution = (736,480)
raw_capture = PiRGBArray(camera)
time.sleep(0.1)

# initialize start driver
driver_start = True

def capture_object():
	camera.capture(raw_capture, format="bgr")
	frame = raw_capture.array
	raw_capture.truncate(0)
	return frame

def stop_camera():
	camera.stop_preview()
	camera.close()

def get_intensity_light():
	data = BUS.read_i2c_block_data(
				DEVICE,
				ONE_TIME_HIGH_RES_MODE
			)
	return convert_to_number(data)

def object_detection():
	return False if GPIO.input(PIN_IR_SENSOR) else True

def start_stop_driver():
	print(driver_start)
	while True:
		if driver_start:
			GPIO.output(PIN_DRIVER_IN1,GPIO.HIGH)
			GPIO.output(PIN_DRIVER_IN2,GPIO.LOW)
		else:
			GPIO.output(PIN_DRIVER_IN1,GPIO.LOW)
			GPIO.output(PIN_DRIVER_IN2,GPIO.LOW)
		time.sleep(0.01)

def clean_up():
	stop_camera()
	GPIO.cleanup()
	pwm_egg_spar.stop()
	pwm_emitter.stop()

def main():
	'''
	1. Get intensity light
		- when intensity in range min, max value then object detection
	2. Objec detection
		- detection object with infrared sensor
	'''
	global driver_start
	frame, egg_quality = None, None
	# get intensity light
	lux_light = get_intensity_light()
	time.sleep(0.3)
	if lux_light in range(LUX_MIN, LUX_MAX+1):
		print(f'Intensity light: {lux_light} LUX')
		# object detection
		detect_object = object_detection()
		if detect_object:
			print('Found Object')
			
			# stop conveyor
			driver_start = False
			print('Driver Stop')
			time.sleep(DELAY_OBJECT_DETECTION)
			print(f'Delay : {DELAY_OBJECT_DETECTION}')

			# capture camera
			frame = capture_object()
			print('Capture Object')
			cv2.imwrite('capture.jpg', frame)
			# classification egg quality

			egg_quality, frame = 'infertile', frame
			print(f'Processing EGG : {egg_quality}')
			time.sleep(1)
			print('Servo Emiter Start')
			set_angle_servo(
				angle = 100,
				pin = PIN_SERVO_EMITTER,
				pwm = pwm_emitter,
			)
			time.sleep(1)
			# Detect Object to start Conveyor
			print('Detect object')
			detect_object = object_detection()
			if not detect_object:
				print(f'Object {detect_object}')
				time.sleep(1)
				print('Servo Emiter Reset')
				reset_angel_servo(
					angle = 100,
					pin = PIN_SERVO_EMITTER,
					pwm = pwm_emitter,
				)
				# start conveyor
				print('Driver start')
				driver_start = True

				if egg_quality == 'fertile':
					angel_egg_spar = 50
				else:
					angel_egg_spar = 100

				# rotate sparator 
				print(f'Servo Sparator Start {angel_egg_spar}')
				set_angle_servo(
					angle = angel_egg_spar,
					pin = PIN_SERVO_EGG_SPAR,
					pwm = pwm_egg_spar,
				)
				time.sleep(2)
				# reset servo sparator
				print('Servo Sparator Reset')
				reset_angel_servo(
					angle = angel_egg_spar,
					pin = PIN_SERVO_EGG_SPAR,
					pwm = pwm_egg_spar,
				)

	
	return frame, egg_quality