import os
import cv2
import time
import smbus
import numpy as np
import RPi.GPIO as GPIO
from picamera import PiCamera
from picamera.array import PiRGBArray
from RaspberryMotors.motors import servos
from .classification import main_process
from .utils import convert_to_number
from config import DEVICE, RESET,\
				POWER_DOWN, POWER_ON,\
				PIN_DRIVER_IN1, PIN_DRIVER_IN2,\
				ONE_TIME_HIGH_RES_MODE,\
				LUX_MIN, LUX_MAX, \
				PIN_IR_SENSOR, \
				DELAY_OBJECT_DETECTION,\
				PIN_SERVO_EGG_SPAR, PIN_SERVO_EMITTER

print('Setup Sensor')

# declaring hidden warnings
GPIO.setwarnings(False)

# declaring the BCM mode of pins
GPIO.setmode(GPIO.BOARD)

# set behaviour of sensors
GPIO.setup(PIN_IR_SENSOR,GPIO.IN) # ir sensor set input
# GPIO.setup(PIN_SERVO_EGG_SPAR, GPIO.OUT) # egg spar set output
# GPIO.setup(PIN_SERVO_EMITTER, GPIO.OUT) # emiter set output
GPIO.setup(PIN_DRIVER_IN1,GPIO.OUT) # driver set output
GPIO.setup(PIN_DRIVER_IN2,GPIO.OUT) # driver set output

GPIO.output(PIN_DRIVER_IN1,GPIO.LOW) # driver set to low/off
GPIO.output(PIN_DRIVER_IN2,GPIO.LOW) # driver set to low/off

# create pwm object
# pwm_egg_spar = GPIO.PWM(PIN_SERVO_EGG_SPAR, 50)
# pwm_egg_spar.start(0)

# pwm_emitter = GPIO.PWM(PIN_SERVO_EMITTER, 50)
# pwm_emitter.start(0)
servo_emitter = servos.servo(PIN_SERVO_EMITTER)
servo_sparator = servos.servo(PIN_SERVO_EGG_SPAR)
# print("Reset Angle Servo")
# servo_emitter.setAngleAndWait(0)
servo_emitter.setAngleAndWait(40)
servo_sparator.setAngleAndWait(40)
# servo_sparator.setAngleAndWait(0)

# declaring Rev 2 Pi uses 1
BUS = smbus.SMBus(1)

# initialize the camera
print('Read Camera')
camera = PiCamera()
camera.resolution = (736,480)
raw_capture = PiRGBArray(camera)

# # set config
# os.system("v4l2-ctl -d /dev/video0 --set-ctrl=focus_automatic_continuous=0")
# os.system("v4l2-ctl -d /dev/video0 --set-ctrl=focus_absolute=130")
# # camera webcam
# camera = cv2.VideoCapture(0)
# camera.set(cv2.CAP_PROP_AUTOFOCUS, 0)
# camera.set(3, 640)
# camera.set(4, 480)
time.sleep(1)

# initialize start driver
driver_start = True

def capture_object():
	camera.capture(raw_capture, format="bgr")
	frame = raw_capture.array
	frame = cv2.rotate(frame, cv2.ROTATE_180)
	raw_capture.truncate(0)
	return frame

def capture_object_webcam():
	frame = []
	start_time = time.time()
	while camera.isOpened():
		ret, image = camera.read();time.sleep(0.05)
		frame = cv2.rotate(image, cv2.ROTATE_180)
		if time.time()-start_time > 2:
			break
	return frame

def stop_camera():
	# camera.stop_preview()
	# camera.close()
	camera.release()

def get_intensity_light():
	data = BUS.read_i2c_block_data(
				DEVICE,
				ONE_TIME_HIGH_RES_MODE
			)
	return convert_to_number(data)

def object_detection():
	return False if GPIO.input(PIN_IR_SENSOR) else True

def start_stop_driver():
	print("Driver Start")
	while True:
		if driver_start:
			GPIO.output(PIN_DRIVER_IN1,GPIO.LOW)
			GPIO.output(PIN_DRIVER_IN2,GPIO.HIGH)
			time.sleep(0.009)
			GPIO.output(PIN_DRIVER_IN1,GPIO.LOW)
			GPIO.output(PIN_DRIVER_IN2,GPIO.LOW)
			time.sleep(0.2)
		else:
			GPIO.output(PIN_DRIVER_IN1,GPIO.LOW)
			GPIO.output(PIN_DRIVER_IN2,GPIO.LOW)
		# time.sleep(0.01)

def clean_up():
	stop_camera()
	GPIO.cleanup()
	# pwm_egg_spar.stop()
	# pwm_emitter.stop()
	servo_emitter.shutdown()
	servo_sparator.shutdown()

servo_emiter_run = False
frame = np.array([])
fertil = 0
infertil = 0

def main():
	'''
	1. Get intensity light
		- when intensity in range min, max value then object detection
	2. Objec detection
		- detection object with infrared sensor
	'''
	global driver_start, servo_emiter_run, frame, fertil, infertil
	egg_quality =  None
	idle_in_process = False

	# get intensity light
	lux_light = get_intensity_light()
	time.sleep(0.3)
	if lux_light in range(LUX_MIN, LUX_MAX+1):
		print(f'Intensity light: {lux_light} LUX')
		# object detection
		detect_object = object_detection()
		while object_detection():
			if not idle_in_process:
				print('Found Object')
				
				# stop conveyor
				driver_start = False
				print('Driver Stop')
				time.sleep(DELAY_OBJECT_DETECTION)
				print(f'Delay : {DELAY_OBJECT_DETECTION}')

				# capture camera
				frame_cap = capture_object()
				print('Capture Object')
				cv2.imwrite('capture.jpg', frame_cap)
				# classification egg quality
				frame, egg_quality = main_process(frame_cap)
				if egg_quality == 'infertil':
					infertil+= 1
				else:
					fertil+=1
					
				print(f'Processing EGG : {egg_quality}')
				time.sleep(1)

				# moving servo emitter
				if not servo_emiter_run:
					print('Servo Emiter Start')
					servo_emitter.setAngleAndWait(0, 1)
					servo_emiter_run = False

				# Detect Object to start Conveyor
				print('Detect object')
				# detect_object = object_detection()
				
				idle_in_process = True

				while True:
					detect_object = object_detection()
					if object_detection(): 
						idle_in_process = False
						break
					print(f'Object not Found {detect_object}')
					time.sleep(1)
					print('Servo Emiter Reset')
					servo_emitter.setAngleAndWait(30, 1)
					# start conveyor
					print('Driver start')
					driver_start = True

					if egg_quality == 'fertil':
						angel_egg_spar = 40
					else:
						angel_egg_spar = 0

					# rotate sparator 
					print(f'Servo Sparator Start {angel_egg_spar}')
					servo_sparator.setAngleAndWait(angel_egg_spar, 2)
					time.sleep(10)
					# reset servo sparator
					print('Servo Sparator Reset')
					servo_sparator.setAngleAndWait(40, 1)
					print('===============================')
					idle_in_process = False
					break
				break
	
	return frame, egg_quality