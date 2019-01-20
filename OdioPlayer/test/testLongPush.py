# coding: utf-8

import os
import time
import vlc
import eyed3
from espeak import espeak
from espeak import core as espeak_core
import RPi.GPIO as GPIO
from Button import Button
from ButtonType import ButtonType

class OdioPlayer(object):

    btnList =(Button(24,23, ButtonType.Home),Button(25,23,ButtonType.Left),Button(26,23,ButtonType.Right),
        Button(23,24,ButtonType.Up),Button(25,24,ButtonType.Down),Button(26,24,ButtonType.Play),
        Button(23,25,ButtonType.VUp),Button(24,25,ButtonType.VDown),Button(26,25,ButtonType.M1),
        Button(23,26,ButtonType.M2),Button(24,26,ButtonType.M3),Button(25,26,ButtonType.M4))
    
    gPioList = (23,24,25,26)
    lenGPIOList = 0
    previousButtonPushedList = []
    buttonPushedList = []
    longPushedDelay = 2
    startPushedTime = 0
    currentPushedTime = 0
    wasLongPush=False

    def __init__(self):

        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)

        self.lenGPIOList = len(self.gPioList)

    def FindButton(self, gpioOut, gpioIn):
        matches = (x for x in self.btnList if x.gpioIn==gpioIn and x.gpioOut==gpioOut)
        return list(matches)

    def CheckButtonGPIO(self, out, in1, in2, in3):
        tmpBtList = []

        GPIO.setup(out, GPIO.OUT)

        GPIO.setup(in1, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        GPIO.setup(in2, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        GPIO.setup(in3, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

        GPIO.output(out, GPIO.HIGH)

        if GPIO.input(in1) == GPIO.HIGH:
            tmpBtList.extend(self.FindButton(out,in1))

        if GPIO.input(in2) == GPIO.HIGH:
            tmpBtList.extend(self.FindButton(out,in2))

        if GPIO.input(in3) == GPIO.HIGH:
            tmpBtList.extend(self.FindButton(out,in3))

        return tmpBtList


    def Start(self):
        try:
            while True:
                i=0
                while i< self.lenGPIOList:
                    tmpBtList = []
                    tmpBtList = self.CheckButtonGPIO(self.gPioList[(0+i)%self.lenGPIOList],
                                                 self.gPioList[(1+i)%self.lenGPIOList],
                                                 self.gPioList[(2+i)%self.lenGPIOList],
                                                 self.gPioList[(3+i)%self.lenGPIOList])
                    if tmpBtList:
                        self.buttonPushedList.extend(tmpBtList)
                    i+=1

                #Si bouton précédent = bouton -> calcul pushed time
                if cmp(self.previousButtonPushedList, self.buttonPushedList) == 0:
                    self.currentPushedTime = time.time()-self.startPushedTime
                    if self.currentPushedTime >= self.longPushedDelay:
                        if  self.buttonPushedList:  
                            tmpBtPushedText=''
                            for bt in self.buttonPushedList:
                                tmpBtPushedText = tmpBtPushedText + '[' + ButtonType.toString(bt.type) +']'
                                #speak(bt.name)
                            print(tmpBtPushedText +" long push")
                            self.currentPushedTime = 0
                            self.startPushedTime = time.time()
                            self.wasLongPush = True
                #Sinon
                else:
                    #Si nouveau bouton -> init pushed time
                    if  self.buttonPushedList: 
                        self.currentPushedTime = 0
                        self.startPushedTime = time.time()
                    #Si pas de bouton (release du bouton)
                    elif self.currentPushedTime < self.longPushedDelay:
                        #print("buttonPushedList: "+str(self.buttonPushedList))
                        #print("previousButtonPushedList: "+str(self.previousButtonPushedList))
                        #print("wasLongPush: "+str(self.wasLongPush))
                        if self.wasLongPush == False:
                            tmpBtPushedText=''
                            for bt in self.previousButtonPushedList:
                                tmpBtPushedText = tmpBtPushedText + '[' + ButtonType.toString(bt.type) +']'
                                #speak(bt.name)
                            print(tmpBtPushedText +" short push")
                        else:
                            self.wasLongPush = False

                self.previousButtonPushedList = list(self.buttonPushedList)
                self.buttonPushedList = []
                time.sleep(0.2)
        except ValueError:
            print (ValueError)
            GPIO.cleanup()

try:
    OdioPlayer().Start()
except ValueError:
    print (ValueError)
    GPIO.cleanup()
