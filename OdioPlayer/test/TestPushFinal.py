import RPi.GPIO as GPIO
import time

class Button:
    def __init__(self, gpioOut, gpioIn, name):
        self.gpioOut = gpioOut
        self.gpioIn = gpioIn
        self.name = name

    def __repr__(self):
        return "({0}-{1}) {2}".format(self.gpioOut, self.gpioIn,self.name)

    def __str__(self):
        return "({0}-{1}) {2}".format(self.gpioOut, self.gpioIn,self.name)

btnList =(Button(24,23,'Home'),Button(25,23,'Left'),Button(26,23,'Right'),
        Button(23,24,'Up'),Button(25,24,'Down'),Button(26,24,'Ok'),
        Button(23,25,'V+'),Button(24,25,'V-'),Button(26,25,'M1'),
        Button(23,26,'M2'),Button(24,26,'M3'),Button(25,26,'M4'))

def FindButton(gpioOut, gpioIn):
    matches = (x for x in btnList if x.gpioIn==gpioIn and x.gpioOut==gpioOut)
    return list(matches)

def CheckButtonGPIO(out, in1, in2, in3):
    btList = []

    GPIO.setup(out, GPIO.OUT)

    GPIO.setup(in1, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    GPIO.setup(in2, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    GPIO.setup(in3, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

    GPIO.output(out, GPIO.HIGH)

    if GPIO.input(in1) == GPIO.HIGH:
        btList.extend(FindButton(out,in1))

    if GPIO.input(in2) == GPIO.HIGH:
        btList.extend(FindButton(out,in2))

    if GPIO.input(in3) == GPIO.HIGH:
        btList.extend(FindButton(out,in3))

    return btList

GPIO.setmode(GPIO.BCM)

gPioList = (23,24,25,26)
lenGPIOList = len(gPioList)

buttonPushedList = []

try:
    while True:
        i=0
        while i< lenGPIOList:
            tmpBtList = []
            tmpBtList = CheckButtonGPIO(gPioList[(0+i)%lenGPIOList],
                                         gPioList[(1+i)%lenGPIOList],
                                         gPioList[(2+i)%lenGPIOList],
                                         gPioList[(3+i)%lenGPIOList])
            if tmpBtList:
                buttonPushedList.extend(tmpBtList)
            i+=1

        if  buttonPushedList:  
            buttonPushedListText=''
            for bt in buttonPushedList:
                buttonPushedListText = buttonPushedListText + '[' + bt.name +']'
            print(buttonPushedListText)
        buttonPushedList = []

        time.sleep(0.2)
except:
    GPIO.cleanup()