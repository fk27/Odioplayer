import os

#isWidows = False

#if os.name == 'nt':
#    isWidows = True

#if isWidows==False:
#    from espeak import espeak
#    espeak.set_voice("fr")
#else:
#    from subprocess import call

#def speak( str ):
#   if isWidows:
#       os.system('espeak -vfr+f3 -s140 "'+str+'"')
#       '''call(["espeak","-vfr+f3 -s140",str])'''
#   else:
#       espeak.synth(str)
#   return

#speak("Odio Player started.")
#os.system('espeak -vfr+f3 -s140 "Odio Player started."')


audioRoot= '/home/pi/Music'
currentVolume = 50
volumeMin = 20
volumeMax = 80
volumeIncr = 5

currentFolder = audioRoot
currentTrackList = []
currentTrackId=0
lastTrackId=0

for filename in os.listdir(currentFolder):
    if filename.endswith(".mp3") or filename.endswith(".flac") or filename.endswith(".wav"):
        #MediaList.add_media(vlcInstance.media_new(audioRoot+'/'+filename))
        currentTrackList.append(currentFolder+'/'+filename)
        print (filename)

lastTrackId = len(currentTrackList)-1

import vlc
vlcInstance = vlc.Instance()
player = vlcInstance.media_player_new()
player.set_media(vlcInstance.media_new(currentTrackList[0]))
player.audio_set_volume(volumeMin)

import RPi.GPIO as GPIO
import time

class Button:
    def __init__(self, gpioOut, gpioIn, type):
        self.gpioOut = gpioOut
        self.gpioIn = gpioIn
        self.type = type
        self.name = str(type)

    def __repr__(self):
        return "({0}-{1}) {2}".format(self.gpioOut, self.gpioIn,self.name)

    def __str__(self):
        return "({0}-{1}) {2}".format(self.gpioOut, self.gpioIn,self.name)

class ButtonType:
    Home = 1
    Left = 2
    Right = 3
    Up = 4
    Down = 5
    Action = 6
    VUp = 7
    VDown = 8
    M1 = 9
    M2 = 10
    M3 = 11
    M4 = 12

btnList =(Button(24,23, ButtonType.Home),Button(25,23,ButtonType.Left),Button(26,23,ButtonType.Right),
        Button(23,24,ButtonType.Up),Button(25,24,ButtonType.Down),Button(26,24,ButtonType.Action),
        Button(23,25,ButtonType.VUp),Button(24,25,ButtonType.VDown),Button(26,25,ButtonType.M1),
        Button(23,26,ButtonType.M2),Button(24,26,ButtonType.M3),Button(25,26,ButtonType.M4))

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
                #speak(bt.name)
            print(buttonPushedListText)

            if len(buttonPushedList)==1:
                if buttonPushedList[0].type == ButtonType.Action:
                    if player.is_playing():
                        player.pause()
                    else:
                        player.play()
                elif buttonPushedList[0].type == ButtonType.Home:
                    player.stop()
                elif buttonPushedList[0].type == ButtonType.Up:
                    currentTrackId = (currentTrackId -1)%lastTrackId
                    player.set_media(vlcInstance.media_new(currentTrackList[currentTrackId]))
                    player.play()
                elif buttonPushedList[0].type == ButtonType.Down:
                    currentTrackId = (currentTrackId +1)%lastTrackId
                    player.set_media(vlcInstance.media_new(currentTrackList[currentTrackId]))
                    player.play()
                #elif buttonPushedList[0].type == ButtonType.Left:
                #elif buttonPushedList[0].type == ButtonType.Right:
                elif buttonPushedList[0].type == ButtonType.VUp:
                    tmpvol = player.audio_get_volume()
                    if tmpvol + volumeIncr < volumeMax: 
                        player.audio_set_volume(tmpvol+volumeIncr)
                    else: 
                        player.audio_set_volume(volumeMax)
                    print(str(player.audio_get_volume()))
                elif buttonPushedList[0].type == ButtonType.VDown:
                    tmpvol=player.audio_get_volume()
                    if tmpvol - volumeIncr > volumeMin: 
                        player.audio_set_volume(tmpvol-volumeIncr)
                    else: 
                        player.audio_set_volume(volumeMin)
                    print(str(player.audio_get_volume()))

        buttonPushedList = []

        time.sleep(0.2)
except:
    GPIO.cleanup()