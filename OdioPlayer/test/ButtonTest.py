import RPi.GPIO as GPIO
import time

'''gpio 23,24,25,26'''

GPIO.setmode(GPIO.BCM)

GPIO.setup(23, GPIO.OUT)
GPIO.setup(24, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(25, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(26, GPIO.IN, pull_up_down=GPIO.PUD_UP)

GPIO.output(23, GPIO.HIGH)

try:
    while True:
        bt1=GPIO.input(24)
        if bt1 == GPIO.LOW:
            print('bt1 ')

        bt2=GPIO.input(25)
        if bt2 == GPIO.LOW:
            print('bt2 ')

        bt3=GPIO.input(26)
        if bt3 == GPIO.LOW:
            print('bt3 ')
        time.sleep(0.2)
except:
    GPIO.cleanup()




