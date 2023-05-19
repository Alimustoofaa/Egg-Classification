import cv2
import time
import smbus
import RPi.GPIO as GPIO
from picamera import PiCamera
from picamera.array import PiRGBArray

from utils import convert_to_number,\
				set_angle_servo, reset_angel_servo

from ..config import DEVICE, RESET,\
				POWER_DOWN, POWER_ON,\
				ONE_TIME_HIGH_RES_MODE,\
				LUX_MIN, LUX_MAX, \
				PIN_IR_SENSOR, \
				DELAY_OBJECT_DETECTION,\
				PIN_SERVO_EGG_SPAR, PIN_SERVO_EMITTER

# declaring Rev 2 Pi uses 1
BUS = smbus.SMBus(1)

# declaring the BCM mode of pins
GPIO.setmode(GPIO.BOARD)

# set behaviour of sensors
GPIO.setup(PIN_IR_SENSOR,GPIO.IN) # ir sensor set input
GPIO.setup(PIN_SERVO_EGG_SPAR, GPIO.OUT) # egg spar set output
GPIO.setup(PIN_SERVO_EMITTER, GPIO.OUT) # emiter set output


# create pwm object
pwm_egg_spar = GPIO.PWM(PIN_SERVO_EGG_SPAR, 50)
pwm_egg_spar.start(0)

pwm_emitter = GPIO.PWM(PIN_SERVO_EMITTER, 50)
pwm_emitter.start(0)


# initialize the camera
camera = PiCamera()
raw_capture = PiRGBArray(camera)
time.sleep(0.1)

def capture_object():
	camera.capture(raw_capture, format="bgr")
	frame = raw_capture.array
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
	return True if GPIO.input(PIN_IR_SENSOR) else False

def start_driver():
	pass
def stop_driver():
	pass

def main(frame=None):
	'''
	1. Get intensity light
		- when intensity in range min, max value then object detection
	2. Objec detection
		- detection object with infrared sensor
	'''
	# get intensity light
	lux_light = get_intensity_light()
	if lux_light in range(LUX_MIN, LUX_MAX+1):
		print(f'Intensity light: {lux_light} LUX')
		# object detection
		detect_object = object_detection()
		if detect_object:
			print('Found Object')
			time.sleep(DELAY_OBJECT_DETECTION)

			# stop conveyor

			# capture camera
			frame = capture_object()

			# classification egg quality

			egg_quality, frame = 'infertile', None

			if egg_quality == 'fertile':
				angel_egg_spar = 100
			else:
				angel_egg_spar = -100

			# rotate sparator 
			set_angle_servo(
				angle = angel_egg_spar,
				pin = PIN_SERVO_EGG_SPAR,
				pwm = pwm_egg_spar,
			)

			# start conveyor low speed

			# reset servo sparator
			reset_angel_servo(
				angle = angel_egg_spar,
				pin = PIN_SERVO_EGG_SPAR,
				pwm = pwm_egg_spar,
			)
