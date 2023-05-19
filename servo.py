from time import sleep
import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BOARD)

PIN_SERVO_EGG_SPAR = 12
PIN_SERVO_EMITTER = 11


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
numLoops = 12
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
GPIO.cleanup()