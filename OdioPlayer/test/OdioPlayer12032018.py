
# encoding=utf8  
import sys  

reload(sys)  
sys.setdefaultencoding('utf8')

import os
import time
import vlc
import eyed3
from espeak import espeak
from espeak import core as espeak_core
from polyglot.detect import Detector
from bs4 import BeautifulSoup
import RPi.GPIO as GPIO

from Button import Button
tmpBtPushedText

class OdioPlayer(object):

    btnList = []
    gPioList = []
    lenGPIOList = 0
    buttonPushedList = []
    previousButtonPushedList = []

    longPushedDelay = 0
    startPushedTime = 0
    currentPushedTime = 0
    wasLongPush=False

    audioRoot= None
 
    safeVolMin=None
    safeVolMax=None
    defaultSafeVol = None

    outdoorVolMin = None
    outdoorVolMax = None
    defaultOutdoorVol = None
    
    volumeMin = None
    volumeMax = None
    currentVolume = None

    volumeIncr = None
    isSafeVolume = True

    currentAlbumList = []
    moduloAlbumList = 0
    currentAlbumPath = None
    currentAlbumId = 0

    currentTrackList = []
    moduloTrackList = 0
    currentTrackId = 0

    lastTrackId = 0
    currentMedia = None
    vlcInstance = None
    player = None
    vlc_events = None

    playNextSong = False
    isSpeaking = False
    playerWasPlaying = False

    savedDataFile = None
    savedData = None
    configFile = None
    config = None
    isDebug = False

    def __init__(self):

        try:
            self.savedDataFile = open("savedData.xml","r+")
            self.savedData = BeautifulSoup(self.savedDataFile,'xml')

            if self.savedData.lastAlbumId.string!=None and self.savedData.lastAlbumTitle.string!=None and self.savedData.lastTrackId.string!=None and self.savedData.lastTrackTitle.string!=None:
                print("lastAlbumId: "+ str(self.savedData.lastAlbumId.string.strip()))
                print("lastAlbumTitle: "+ str(self.savedData.lastAlbumTitle.string.strip()))
                print("lastTrackId: "+ str(self.savedData.lastTrackId.string.strip()))
                print("lastTrackTitle: "+ str(self.savedData.lastTrackTitle.string.strip()))

            self.configFile = open("config.xml")
            self.config = BeautifulSoup(self.configFile,'xml')

            self.isDebug = True if self.config.isDebug.string == "True" else False
            print("self.isDebug: "+str(self.isDebug))
            self.audioRoot = self.config.audioRoot.string

            self.safeVolMin=int(self.config.volume.safeVolMin.string)
            self.safeVolMax=int(self.config.volume.safeVolMax.string)
            self.defaultSafeVol = int(self.config.volume.defaultSafeVol.string)

            self.outdoorVolMin = int(self.config.volume.outdoorVolMin.string)
            self.outdoorVolMax = int(self.config.volume.outdoorVolMax.string)
            self.defaultOutdoorVol = int(self.config.volume.defaultOutdoorVol.string)

            self.volumeIncr = int(self.config.volume.volumeIncr.string)

            self.volumeMin = self.safeVolMin
            self.volumeMax = self.safeVolMax

            if self.savedData.currentVolume.string != None:
                self.currentVolume = int(self.savedData.currentVolume.string)
            else:
                self.currentVolume = self.defaultSafeVol
            print("currentVolume: "+ str(self.currentVolume))

            GPIO.setwarnings(True if self.config.gpio.setWarnings.string == "True" else False)
            GPIO.setmode(GPIO.BCM)

            for gpioId in self.config.gpio.gPioList.findAll('id'):
                self.gPioList.append(int(gpioId.string))

            self.lenGPIOList = len(self.gPioList)

            self.btnList = []
            for button in self.config.buttons.findAll('button'):
                self.btnList.append(Button(int(button["gpioOut"]), int(button["gpioIn"]), ButtonType[button["type"]]))
        
            self.longPushedDelay = int(self.config.buttons.longPushedDelay.string)

            self.vlcInstance = vlc.Instance()
            self.player = self.vlcInstance.media_player_new()
            self.player.audio_set_volume(self.currentVolume)
            self.vlc_events = self.player.event_manager()
            self.vlc_events.event_attach(vlc.EventType.MediaPlayerBackward.MediaPlayerEndReached, self.AutoPlayNext)

            self.currentAlbumList = self.GetAlbumList(self.audioRoot)
            self.moduloAlbumList = len(self.currentAlbumList)

            self.Speak("Lecteur Odio démarré")

            if self.savedData.lastAlbumId.string != None and self.savedData.lastAlbumTitle.string != None:
               
                lastAlbumId = int(self.savedData.lastAlbumId.string)
                lastAlbumTitle = self.savedData.lastAlbumTitle.string.strip()

                if lastAlbumId < self.moduloAlbumList and self.currentAlbumList[lastAlbumId]==lastAlbumTitle:
                    print("lastAlbum trouvé : "+str(lastAlbumId))
                    self.currentAlbumId = lastAlbumId
                    self.currentTrackId = int(self.savedData.lastTrackId.string)

                    self.PlayAlbum(self.currentAlbumId)

            else:
                self.currentAlbumId = 0
                self.currentTrackId = 0
                self.PlayAlbum(self.currentAlbumId)


        except ValueError:
            if self.isDebug:
                print(ValueError)
        
    def Speak(self, text):

        if self.player.is_playing():
            self.player.stop()
            self.playerWasPlaying=True

        while self.isSpeaking:
            time.sleep(0.2)

        self.isSpeaking = True

        def Speak_Callback(event, pos, length):
            if event == espeak_core.event_MSG_TERMINATED:
                self.isSpeaking = False
                #print("speak finished")
                if self.playerWasPlaying:
                    self.player.play()
                    self.playerWasPlaying = False

        #try:
        #    detector = Detector(text)
        #    print("language détectée: "+ str(detector.language))
        #    lg = detector.language.code
        #    if lg == 'en':
        #        espeak.set_voice("mb-en1")
        #    else:
        #        espeak.set_voice("mb-fr1")
        #except ValueError as e:
        #    print (e)
        #    espeak.set_voice("mb-fr1")

        espeak.set_voice("mb-fr1")
        espeak.set_parameter(espeak.Parameter.Rate,140)
        espeak.set_parameter(espeak.Parameter.Pitch,20)
        espeak.set_parameter(espeak.Parameter.Volume, self.currentVolume)

        espeak.set_SynthCallback(Speak_Callback)
  
        call_result = espeak.synth(text)

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

                if self.playNextSong == True:
                    self.PlayNext()
                    self.playNextSong = False

                if  self.buttonPushedList:  
                    tmpBtPushedText=''
                    for bt in self.buttonPushedList:
                        tmpBtPushedText = tmpBtPushedText + '[' + ButtonType.toString(bt.type) +']'
                        #speak(bt.name)
                    print(tmpBtPushedText)

                    if len(self.buttonPushedList)==2:
                        if len(filter(lambda x: (x.type == ButtonType.VUp or x.type == ButtonType.VDown ), self.buttonPushedList))==2:
                            if cmp(self.previousButtonPushedList, self.buttonPushedList) == 0:
                                self.currentPushedTime = time.time()-self.startPushedTime
                                if self.currentPushedTime >= self.longPushedDelay:
                                    if self.isSafeVolume:
                                        self.SetOutdoorVolume(True)
                                    else:
                                        self.SetOutdoorVolume(False)
                                    self.startPushedTime = time.time()
                            else:
                                self.startPushedTime = time.time()

                    if len(self.buttonPushedList)==1:
                        if self.buttonPushedList[0].type == ButtonType.Play:
                            if self.player.is_playing():
                                self.player.pause()
                            else:
                                self.player.play()
                        elif self.buttonPushedList[0].type == ButtonType.Up:
                            self.PlayPreviousAlbum()
                        elif self.buttonPushedList[0].type == ButtonType.Down:
                            self.PlayNextAlbum()
                        elif self.buttonPushedList[0].type == ButtonType.Left:
                            self.PlayPrevious()
                        elif self.buttonPushedList[0].type == ButtonType.Right:
                            self.PlayNext()
                        elif self.buttonPushedList[0].type == ButtonType.VUp:
                            self.VolumeUp()
                        elif self.buttonPushedList[0].type == ButtonType.VDown:
                            self.VolumeDown()
                        elif self.buttonPushedList[0].type == ButtonType.M1 \
                          or self.buttonPushedList[0].type == ButtonType.M2 \
                          or self.buttonPushedList[0].type == ButtonType.M3 \
                          or self.buttonPushedList[0].type == ButtonType.M4:
                            if cmp(self.previousButtonPushedList, self.buttonPushedList) == 0:
                                self.currentPushedTime = time.time()-self.startPushedTime
                                if self.currentPushedTime >= self.longPushedDelay:
                                    self.MemCurrentAlbum(self.buttonPushedList[0].type)
                            else:
                                self.startPushedTime = time.time()
                self.previousButtonPushedList = list(self.buttonPushedList)
                self.buttonPushedList = []
                time.sleep(0.2)
        except ValueError:
            print (ValueError)
            GPIO.cleanup()

    def Start2(self):
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

                if self.playNextSong == True:
                    self.PlayNext()
                    self.playNextSong = False

                #Si bouton précédent = bouton -> calcul pushed time
                if cmp(self.previousButtonPushedList, self.buttonPushedList) == 0:
                    self.currentPushedTime = time.time()-self.startPushedTime
                    #Si le delay long pushed est dépassé --> execute action long button pushed
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
                            self.ExecuteLongButtonAction(self.buttonPushedList)
                #Si bouton précédent != bouton -> release du bouton OU nouveau bouton poussé
                else:
                    #Si nouveau bouton -> init pushed time
                    if  self.buttonPushedList: 
                        self.currentPushedTime = 0
                        self.startPushedTime = time.time()
                    #Si pas de bouton (release du bouton) => previous button short pushed
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
                            self.ExecuteShortButtonAction(self.previousButtonPushedList)
                        else:
                            self.wasLongPush = False

                self.previousButtonPushedList = list(self.buttonPushedList)
                self.buttonPushedList = []
                time.sleep(0.2)
        except ValueError:
            print (ValueError)
            GPIO.cleanup()

    def ExecuteLongButtonAction(self, btnList):
        if btnList:
            if len(btnList)==1:
                if btnList[0].type == ButtonType.M1 \
                    or btnList[0].type == ButtonType.M2 \
                    or btnList[0].type == ButtonType.M3 \
                    or btnList[0].type == ButtonType.M4:

                    self.MemCurrentAlbum(self.btnList[0].type)

            if len(btnList)==2:
                if len(filter(lambda x: (x.type == ButtonType.VUp or x.type == ButtonType.VDown ), btnList))==2:
                    if self.isSafeVolume:
                        self.SetOutdoorVolume(True)
                    else:
                        self.SetOutdoorVolume(False)

    def ExecuteShortButtonAction(self, btnList):

        if btnList:
            if len(btnList)==1:
                if btnList[0].type == ButtonType.Play:
                    if self.player.is_playing():
                        self.player.pause()
                    else:
                        self.player.play()
                elif btnList[0].type == ButtonType.Up:
                    self.PlayPreviousAlbum()
                elif btnList[0].type == ButtonType.Down:
                    self.PlayNextAlbum()
                elif btnList[0].type == ButtonType.Left:
                    self.PlayPrevious()
                elif btnList[0].type == ButtonType.Right:
                    self.PlayNext()
                elif btnList[0].type == ButtonType.VUp:
                    self.VolumeUp()
                elif btnList[0].type == ButtonType.VDown:
                    self.VolumeDown()
                elif btnList[0].type == ButtonType.M1 \
                    or btnList[0].type == ButtonType.M2 \
                    or btnList[0].type == ButtonType.M3 \
                    or btnList[0].type == ButtonType.M4:
                        print("Play: " + ButtonType.toString(btnList[0].type))

       

    def MemCurrentAlbum (self, btnType):
        #print("btnType: "+ ButtonType.toString(btnType).lower())
        print("-> MemCurrentAlbum")
        if self.savedDataFile.closed:
            self.savedDataFile = open(self.savedDataFile.name,"r+")

        if btnType == ButtonType.M1:
            self.savedData.m1.albumId.string=str(self.currentAlbumId)
            self.savedData.m1.albumTitle.string=str(self.currentAlbumList[self.currentAlbumId])
            self.savedData.m1.trackId.string=str(self.currentTrackId)
            self.savedData.m1.trackTitle.string=str(self.currentTrackList[self.currentTrackId])
        elif btnType == ButtonType.M2:
            self.savedData.m2.albumId.string=str(self.currentAlbumId)
            self.savedData.m2.albumTitle.string=str(self.currentAlbumList[self.currentAlbumId])
            self.savedData.m2.trackId.string=str(self.currentTrackId)
            self.savedData.m2.trackTitle.string=str(self.currentTrackList[self.currentTrackId])
        elif btnType == ButtonType.M3:
            self.savedData.m3.albumId.string=str(self.currentAlbumId)
            self.savedData.m3.albumTitle.string=str(self.currentAlbumList[self.currentAlbumId])
            self.savedData.m3.trackId.string=str(self.currentTrackId)
            self.savedData.m3.trackTitle.string=str(self.currentTrackList[self.currentTrackId])
        elif btnType == ButtonType.M4:
            self.savedData.m4.albumId.string=str(self.currentAlbumId)
            self.savedData.m4.albumTitle.string=str(self.currentAlbumList[self.currentAlbumId])
            self.savedData.m4.trackId.string=str(self.currentTrackId)
            self.savedData.m4.trackTitle.string=str(self.currentTrackList[self.currentTrackId])
        
        self.savedDataFile.seek(0)
        self.savedDataFile.truncate()
        self.savedDataFile.write(self.savedData.prettify())
        self.savedDataFile.close()

    def SaveCurrentAlbum (self):
        print("-> SaveCurrentAlbum")
        if self.savedDataFile.closed:
            self.savedDataFile = open(self.savedDataFile.name,"r+")

        self.savedData.lastAlbumId.string=str(self.currentAlbumId)
        self.savedData.lastAlbumTitle.string=str(self.currentAlbumList[self.currentAlbumId])
        self.savedData.lastTrackId.string=str(self.currentTrackId)
        self.savedData.lastTrackTitle.string=str(self.currentTrackList[self.currentTrackId])
        
        self.savedDataFile.seek(0)
        self.savedDataFile.truncate()
        self.savedDataFile.write(self.savedData.prettify())
        self.savedDataFile.close()

    def SaveCurrentVolume (self):
        print("-> SaveCurrentVolume: "+str(self.currentVolume))
        if self.savedDataFile.closed:
            self.savedDataFile = open(self.savedDataFile.name,"r+")

        self.savedData.currentVolume.string = str(self.currentVolume)

        self.savedDataFile.seek(0)
        self.savedDataFile.truncate()
        self.savedDataFile.write(self.savedData.prettify())
        self.savedDataFile.close()


    def SetOutdoorVolume (self, value):
        if value:
            self.volumeMin = self.outdoorVolMin
            self.volumeMax = self.outdoorVolMax
            self.currentVolume = self.defaultOutdoorVol
            self.isSafeVolume = False
            self.player.audio_set_volume(self.currentVolume)
            self.Speak("Mode Son Extérieur")
        else:
            self.volumeMin = self.safeVolMin
            self.volumeMax = self.safeVolMax
            self.currentVolume = self.defaultSafeVol
            self.isSafeVolume = True
            self.player.audio_set_volume(self.currentVolume)
            self.Speak("Mode Son Sécurisé")
        
    def contains(list, filter):
        for x in list:
            if filter(x):
                return True
        return False

    def GetAlbumList(self, folder):
        tmpList = []

        for subfolder in os.listdir(folder):
            subfolderPath = folder + '/' + subfolder
            if os.path.isdir(subfolderPath):
                tmpList.append(subfolder)

        tmpList = sorted(tmpList)
        print("*** Albums ***")
        for subfolder in tmpList:
            print("-> "+subfolder)
        print("******")
        return tmpList

    def PlayAlbum(self, albumId):
        self.Speak(self.currentAlbumList[self.currentAlbumId])
        print ("Playing Album:"+ self.currentAlbumList[albumId])

        self.currentAlbumPath = self.audioRoot+"/"+ self.currentAlbumList[albumId]
        self.currentTrackList = self.GetTrackList(self.currentAlbumPath)
        self.moduloTrackList = len(self.currentTrackList)

        if self.moduloTrackList > 0:
            self.currentMedia = self.vlcInstance.media_new(self.currentAlbumPath +"/"+ self.currentTrackList[self.currentTrackId])
            self.player.set_media(self.currentMedia)

    def PlayNextAlbum(self):
        self.currentAlbumId = (self.currentAlbumId +1)%self.moduloAlbumList
        self.currentTrackId = 0
        self.PlayAlbum(self.currentAlbumId)

    def PlayPreviousAlbum(self):
        self.currentAlbumId = (self.currentAlbumId -1)%self.moduloAlbumList
        self.currentTrackId = 0
        self.PlayAlbum(self.currentAlbumId)

    def GetTrackList(self, folder):
        tmpList = []
        for filename in os.listdir(folder):
            if filename.endswith(".mp3") or filename.endswith(".flac") or filename.endswith(".wav"):
                tmpList.append(filename)

        tmpList = sorted(tmpList)

        print("*** Tracks ***")
        for track in tmpList:
            print("-> "+track)
        print("******")

        return tmpList

    def GetTrackTitle (self, track):
        title = None
        try:
            audiofile = eyed3.load(track)
            if audiofile != None and audiofile.tag.title:
                title = audiofile.tag.title
            else:
                title = os.path.splitext(os.path.basename(track))[0]
        except ValueError:
            print (ValueError)
        return title

    def AutoPlayNext(self, event):
        self.playNextSong = True

    def Play(self, trackId):
        self.player.stop()

        trackTitle  = self.GetTrackTitle(self.currentAlbumPath +"/"+ self.currentTrackList[trackId])
        
        if trackTitle != None:
            print(trackTitle)
            self.Speak(trackTitle)

        while self.isSpeaking:
            time.sleep(0.2)

        self.currentMedia = self.vlcInstance.media_new(self.currentAlbumPath +"/"+ self.currentTrackList[trackId])
        self.player.set_media(self.currentMedia)
        self.player.play()

        self.SaveCurrentAlbum()

    def PlayNext(self):
        #print("PlayNext")
        self.currentTrackId = (self.currentTrackId +1)%self.moduloTrackList
        self.Play(self.currentTrackId)

    def PlayPrevious(self):
        #print("PlayPrevious")
        self.currentTrackId = (self.currentTrackId -1)%self.moduloTrackList
        self.Play(self.currentTrackId)

    def VolumeUp(self):

        if self.currentVolume + self.volumeIncr < self.volumeMax: 
            self.currentVolume = self.currentVolume + self.volumeIncr
        else: 
            self.currentVolume = self.volumeMax

        self.player.audio_set_volume(self.currentVolume)

        self.SaveCurrentVolume()

        print(str(self.player.audio_get_volume()))

    def VolumeDown(self):
        if self.currentVolume - self.volumeIncr > self.volumeMin: 
            self.currentVolume = self.currentVolume - self.volumeIncr
        else: 
            self.currentVolume = self.volumeMin

        self.player.audio_set_volume(self.currentVolume)

        self.SaveCurrentVolume()

        print(str(self.player.audio_get_volume()))

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

try:
    OdioPlayer().Start2()
except ValueError:
    print (ValueError)
    GPIO.cleanup()