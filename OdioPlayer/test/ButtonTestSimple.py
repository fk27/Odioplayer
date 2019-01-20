import RPi.GPIO as GPIO
import time

'''gpio 23,24,25,26'''

GPIO.setmode(GPIO.BCM)

GPIO.setup(23, GPIO.OUT)
GPIO.setup(24, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(25, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(26, GPIO.IN, pull_up_down=GPIO.PUD_UP)

GPIO.output(23, True)

try:
    while True:
        bt1=GPIO.input(24)
        if bt1 == False:
            print('bt1:false ')

        bt2=GPIO.input(25)
        if bt2 == False:
            print('bt2:false ')

        bt3=GPIO.input(26)
        if bt3 == False:
            print('bt3:false ')
        time.sleep(0.2)
except:
    GPIO.cleanup()




