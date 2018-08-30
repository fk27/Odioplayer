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
    buttonPushedList = []

    audioRoot= '/home/pi/Music'
    currentVolume = 20
    volumeMin = 0
    volumeMax = 80
    volumeIncr = 5

    currentFolder = audioRoot

    currentArtistList = []
    moduloArtistList = 0
    currentArtistId = 0

    currentAlbumList = []
    moduloAlbumList = 0
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
    changeArtist = False
    isSpeaking = False

    def __init__(self):

        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)

        self.lenGPIOList = len(self.gPioList)

        self.vlcInstance = vlc.Instance()
        self.player = self.vlcInstance.media_player_new()
        self.player.audio_set_volume(self.volumeMin)
        self.vlc_events = self.player.event_manager()
        self.vlc_events.event_attach(vlc.EventType.MediaPlayerBackward.MediaPlayerEndReached, self.AutoPlayNext)

        self.currentArtistList = self.GetArtistList(self.currentFolder)
        self.moduloArtistList = len(self.currentArtistList)
        self.PlayArtist(self.currentArtistId)

        self.Speak("Lecteur Odio démarré")
        
    def Speak(self, str):
        self.isSpeaking = True

        def Speak_Callback(event, pos, length):
            if event == espeak_core.event_MSG_TERMINATED:
                self.isSpeaking = False
                print("speak finished")

        espeak.set_voice("mb-fr1")
        espeak.set_parameter(espeak.Parameter.Rate,140)
        espeak.set_parameter(espeak.Parameter.Pitch,20)
        espeak.set_parameter(espeak.Parameter.Volume,self.currentVolume)

        espeak.set_SynthCallback(Speak_Callback)
  
        call_result = espeak.synth(str)

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
                    if tmpBtList:CheckButtonGPIO
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

                    if len(self.buttonPushedList)==1:
                        if self.buttonPushedList[0].type == ButtonType.Play:
                            if self.changeArtist:
                                self.changeArtist = False

                            if self.player.is_playing():
                                self.player.pause()
                            else:
                                self.player.play()
                        elif self.buttonPushedList[0].type == ButtonType.Home:
                            self.Speak("Veux-tu choisir un autre artiste?")
                            self.player.stop()
                            self.changeArtist = True
                        elif self.buttonPushedList[0].type == ButtonType.Up:
                            if self.changeArtist:
                                self.PlayPreviousArtist()
                            else:
                                self.PlayPreviousAlbum()
                        elif self.buttonPushedList[0].type == ButtonType.Down:
                            if self.changeArtist:
                                self.PlayNextArtist()
                            else:
                                self.PlayNextAlbum()
                        elif self.buttonPushedList[0].type == ButtonType.Left:
                            self.PlayPrevious()
                        elif self.buttonPushedList[0].type == ButtonType.Right:
                            self.PlayNext()
                        elif self.buttonPushedList[0].type == ButtonType.VUp:
                            self.VolumeUp()
                        elif self.buttonPushedList[0].type == ButtonType.VDown:
                            self.VolumeDown()
                self.buttonPushedList = []
                time.sleep(0.2)
        except ValueError:
            print (ValueError)
            GPIO.cleanup()

    def GetArtistList(self, folder):
        tmpList = []
        for subfolder in os.listdir(folder):
            subfolderPath = folder + '/' + subfolder
            if os.path.isdir(subfolderPath):
                tmpList.append(subfolder)
                print ("Artist: " + subfolder)
        return tmpList  
    
    def PlayArtist(self, artistId):
        print ("Current Artist:"+ self.currentArtistList[artistId])
        self.currentAlbumList = self.GetAlbumList(self.audioRoot+"/"+self.currentArtistList[artistId])
        self.moduloAlbumList = len(self.currentAlbumList)

        if self.currentAlbumList>0:
            self.currentAlbumId = 0
            self.PlayAlbum(self.currentAlbumId)

    def PlayNextArtist(self):
        self.currentArtistId = (self.currentArtistId +1)%self.moduloArtistList
        self.Speak("Artiste suivant: "+ self.currentArtistList[self.currentArtistId])
        self.PlayArtist(self.currentArtistId)

    def PlayPreviousArtist(self):
        self.currentArtistId = (self.currentArtistId -1)%self.moduloArtistList
        self.Speak("Artiste précédent: "+ self.currentArtistList[self.currentArtistId])
        self.PlayArtist(self.currentArtistId)

    def GetAlbumList(self, folder):
        tmpList = []
        for subfolder in os.listdir(folder):
            subfolderPath = folder + '/' + subfolder
            if os.path.isdir(subfolderPath):
                tmpList.append(subfolder)
                print ("Album: " + subfolder)
        return tmpList

    def PlayAlbum(self, albumId):
        print ("Current Album:"+ self.currentAlbumList[albumId])
        self.currentTrackList = self.GetTrackList(self.currentAlbumList[albumId])
        self.moduloTrackList = len(self.currentTrackList)

        if self.moduloTrackList>0:
            self.currentMedia = self.vlcInstance.media_new(self.currentTrackList[0])
            self.player.set_media(self.currentMedia)

    def PlayNextAlbum(self):
        self.currentAlbumId = (self.currentAlbumId +1)%self.moduloAlbumList
        self.Speak("Album suivant: "+ self.currentAlbumList[self.currentAlbumId])
        self.PlayAlbum(self.currentAlbumId)

    def PlayPreviousAlbum(self):
        self.currentAlbumId = (self.currentAlbumId -1)%self.moduloAlbumList
        self.Speak("Album précédent: "+ self.currentAlbumList[self.currentAlbumId])
        self.PlayAlbum(self.currentAlbumId)

    def GetTrackList(self, folder):
        tmpList = []
        for filename in os.listdir(folder):
            if filename.endswith(".mp3") or filename.endswith(".flac") or filename.endswith(".wav"):
                tmpList.append(folder+'/'+filename)
                print (filename)
        return tmpList

    def DisplayTrackInfo (self, track):
        #audiofile = eyed3.load(track)
        #audiofile.tag.artist = u"Integrity"
        #audiofile.tag.album = u"Humanity Is The Devil"
        #audiofile.tag.album_artist = u"Integrity"
        #audiofile.tag.title = u"Hollow"
        #audiofile.tag.track_num = 2

        #try:
        #    audiofile = eyed3.load(track)
        #    if audiofile != None and audiofile.tag.title:
        #        print (audiofile.tag.title)
        #    else:
        #        print(os.path.splitext(os.path.basename(track))[0])
        #except ValueError:
        #    print (ValueError)

        print(os.path.splitext(os.path.basename(track))[0])
        #self.Speak(os.path.splitext(os.path.basename(track))[0])
        self.Speak(os.path.splitext(os.path.basename(track))[0])

    def AutoPlayNext(self, event):
        self.playNextSong = True

    def Play(self, trackId):
        #self.DisplayTrackInfo(self.currentTrackList[trackId])
       
        while self.isSpeaking:
            time.sleep(0.2)

        self.currentMedia = self.vlcInstance.media_new(self.currentTrackList[trackId])
        self.player.set_media(self.currentMedia)
        self.player.play()

    def PlayNext(self):
        #print("PlayNext")
        self.currentTrackId = (self.currentTrackId +1)%self.moduloTrackList
        self.Play(self.currentTrackId)

    def PlayPrevious(self):
        #print("PlayPrevious")
        self.currentTrackId = (self.currentTrackId -1)%self.moduloTrackList
        self.Play(self.currentTrackId)

    def VolumeUp(self):
        tmpvol = self.player.audio_get_volume()
        if tmpvol + self.volumeIncr < self.volumeMax: 
            self.player.audio_set_volume(tmpvol+self.volumeIncr)
        else: 
            self.player.audio_set_volume(self.volumeMax)
        print(str(self.player.audio_get_volume()))

    def VolumeDown(self):
        tmpvol = self.player.audio_get_volume()
        if tmpvol - self.volumeIncr > self.volumeMin: 
            self.player.audio_set_volume(tmpvol-self.volumeIncr)
        else: 
            self.player.audio_set_volume(self.volumeMin)
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
    OdioPlayer().Start()
except ValueError:
    print (ValueError)
    GPIO.cleanup()
