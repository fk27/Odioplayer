import os
import sys, getopt
import time
import vlc
import eyed3
from bs4 import BeautifulSoup
import RPi.GPIO as GPIO

from lipopi import *

from Button import Button
from ButtonType import ButtonType

class OdioPlayer(object):

    debug = False
    quiet = False

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
    currentVolume = 50

    volumeIncr = None
    isSafeVolume = True

    currentAlbumList = []
    moduloAlbumList = 0
    currentAlbumPath = None
    currentAlbumId = 0

    currentTrackList = []
    moduloTrackList = 0
    currentTrackId = 0
    currentTrackPosition = 0

    lastTrackId = 0
    currentMedia = None
    vlcInstance = None
    player = None
    vlc_events = None

    playNextTrack = False
    global isSpeaking
    isSpeaking = False
    playerWasPlaying = False

    savedDataFile = None
    savedData = None
    configFile = None
    config = None
    isDebug = False
    isAlbumTitleTTS = False
    isSongTitleTTS = False

    applicationPath=''


    def __init__(self, quiet, debug):
        try:
            self.quiet = quiet
            self.debug = debug

            if self.debug:
                print ("-> OdioPlayer: init")

            self.applicationPath = os.path.dirname(os.path.abspath(__file__))
            
            self.savedDataFile = open(self.applicationPath+"/savedData.xml","r+")
            self.savedData = BeautifulSoup(self.savedDataFile,'xml')

            self.configFile = open(self.applicationPath+"/config.xml")
            self.config = BeautifulSoup(self.configFile,'xml')
          
            # if xml files valid --> init param
            if self.savedData.lastAlbumId and self.config.audioRoot:

                #Init parameters
                self.isDebug = True if self.config.isDebug and self.config.isDebug.string == "True" else False
                self.isAlbumTitleTTS = True if self.config.isAlbumTitleTTS and self.config.isAlbumTitleTTS.string == "True" else False
                self.isSongTitleTTS = True if self.config.isSongTitleTTS and self.config.isSongTitleTTS.string == "True" else False
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
            
                #Init GPIO and Buttons
                GPIO.setwarnings(True if self.config.gpio.setWarnings.string == "True" else False)
                GPIO.setmode(GPIO.BCM)

                for gpioId in self.config.gpio.gPioList.findAll('id'):
                    self.gPioList.append(int(gpioId.string))

                self.lenGPIOList = len(self.gPioList)

                self.btnList = []
                for button in self.config.buttons.findAll('button'):
                    self.btnList.append(Button(int(button["gpioOut"]), int(button["gpioIn"]), ButtonType[button["type"]]))
        
                self.longPushedDelay = int(self.config.buttons.longPushedDelay.string)

                #Init VLC
                self.vlcInstance = vlc.Instance()
                self.player = self.vlcInstance.media_player_new()
                self.player.audio_set_volume(self.currentVolume)
                self.vlc_events = self.player.event_manager()
                self.vlc_events.event_attach(vlc.EventType.MediaPlayerBackward.MediaPlayerEndReached, self.AutoPlayNextTrack)

                #Init Album List
                self.currentAlbumList = self.GetAlbumList(self.audioRoot)
                self.moduloAlbumList = len(self.currentAlbumList)

                #If last album exist -> continue to play
                if self.moduloAlbumList>0:
                    if self.savedData.lastAlbumId.string is not None and self.savedData.lastAlbumTitle.string is not None:
               
                        lastAlbumId = int(self.savedData.lastAlbumId.string)
                        lastAlbumTitle = self.savedData.lastAlbumTitle.string.strip()

                        if lastAlbumId < self.moduloAlbumList and self.currentAlbumList[lastAlbumId]==lastAlbumTitle:
                            if self.debug:
                                print("-> Odioplayer: last listened album found - "+str(lastAlbumId))
                            #self.PlayAlbum(lastAlbumId, int(self.savedData.lastTrackId.string), float(self.savedData.lastTrackPosition.string))
                            self.PlayAlbum(lastAlbumId, int(0), float(0))
                    #Else play first album
                    else:
                        self.PlayAlbum(0)
                else:
                    if self.debug:
                        print("-> Odioplayer Error: Aucun album présent")
            else:
                if self.debug:
                    print("Odioplayer Error: savedData.xml ou config.xml not valid")
                self.ReInitSavedDataFile()
                self.__init__()

        except ValueError:
            print("ValueError:")
            print(ValueError)
            self.CleanUp()
        except SystemExit:  
            print("SystemExit:")
            self.CleanUp()
            pass
    
    def CleanUp(self):
        if self.debug:
            print("-> OdioPlayer: CleanUp")
        self.player.stop()
        os.system("sudo sh /home/pi/stopSoundCard.sh")
        GPIO.cleanup()

    def Start(self):
        if self.player:
            try:
                while True:
                    if self.player.is_playing():
                        self.SaveCurrentTrackPosition()
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

                    if self.playNextTrack == True:
                        self.PlayNextTrack()
                        self.playNextTrack = False
                    #print("check")
                    #Si bouton précédent = bouton -> calcul pushed time
                    
                    #ToCheck
                    #if cmp(self.previousButtonPushedList, self.buttonPushedList) == 0:
                    if(self.previousButtonPushedList > self.buttonPushedList) - (self.previousButtonPushedList < self.buttonPushedList) == 0:
                        self.currentPushedTime = time.time()-self.startPushedTime
                        #Si le delay long pushed est dépassé --> execute action long button pushed
                        if self.currentPushedTime >= self.longPushedDelay:
                            if  self.buttonPushedList:  
                                tmpBtPushedText=Button.GetButtonListName(self.buttonPushedList)
                                if self.debug:
                                    print("-> OdioPlayer: " + tmpBtPushedText +" long push")
                                self.currentPushedTime = 0
                                self.startPushedTime = time.time()
                                self.wasLongPush = True
                                self.ExecuteLongButtonAction(self.buttonPushedList)
                        else:
                            btnNumber = len(self.buttonPushedList)
                            #one button long pushed
                            if btnNumber==1:
                                if self.buttonPushedList[0].type != ButtonType.M1 \
                                    and self.buttonPushedList[0].type != ButtonType.M2 \
                                    and self.buttonPushedList[0].type != ButtonType.M3 \
                                    and self.buttonPushedList[0].type != ButtonType.M4:
                                        if self.debug:
                                            print("-> OdioPlayer: long push short action")
                                        self.ExecuteShortButtonAction(self.buttonPushedList)

                    #Si bouton précédent != bouton -> release du bouton OU nouveau bouton poussé
                    else:
                        #Si nouveau bouton -> init pushed time
                        if  self.buttonPushedList: 
                            self.currentPushedTime = 0
                            self.startPushedTime = time.time()
                        #Si pas de bouton (release du bouton) => previous button short pushed
                        elif self.currentPushedTime < self.longPushedDelay:
                            #Si on ne succède pas au release d'un longpush -> vrai release short push
                            if self.wasLongPush == False:
                                tmpBtPushedText=Button.GetButtonListName(self.previousButtonPushedList)
                                if self.debug:
                                    print(tmpBtPushedText +" short push")
                                self.ExecuteShortButtonAction(self.previousButtonPushedList)
                            else:
                                self.wasLongPush = False

                    self.previousButtonPushedList = list(self.buttonPushedList)
                    self.buttonPushedList = []
                    time.sleep(0.1)
            except ValueError:
                print ("ValueError:")
                print (ValueError)
                self.CleanUp()
        else:
            if self.debug:
                print("-> Odioplayer Error: VLC player not initialized")

    def ExecuteLongButtonAction(self, btnList):
        if btnList:
            btnNumber = len(btnList)
            #one button long pushed
            if btnNumber==1:
                if btnList[0].type == ButtonType.M1 \
                    or btnList[0].type == ButtonType.M2 \
                    or btnList[0].type == ButtonType.M3 \
                    or btnList[0].type == ButtonType.M4:

                    self.MemCurrentAlbum(btnList[0].type)
            
            #two buttons long pushed
            if btnNumber==2:
                if len(filter(lambda x: (x.type == ButtonType.VUp or x.type == ButtonType.VDown ), btnList))==2:
                    if self.isSafeVolume:
                        self.SetOutdoorVolume(True)
                    else:
                        self.SetOutdoorVolume(False)

    def ExecuteShortButtonAction(self, btnList):
        if btnList:
            btnNumber = len(btnList)
            if btnNumber==1:
                if btnList[0].type == ButtonType.Play:
                    print("is_playing: "+str(self.player.is_playing()))
                    print("currentTrackId: "+str(self.currentTrackId))
                    print("currentTrackPosition: "+str(self.currentTrackPosition))
                    if self.player.is_playing():
                        print("-> player pause")
                        self.player.pause()
                    else:
                        print("-> player play")
                        self.player.play()

                elif btnList[0].type == ButtonType.Up:
                    self.PlayPreviousAlbum()
                elif btnList[0].type == ButtonType.Down:
                    self.PlayNextAlbum()
                elif btnList[0].type == ButtonType.Left:
                    self.PlayPreviousTrack()
                elif btnList[0].type == ButtonType.Right:
                    self.PlayNextTrack()
                elif btnList[0].type == ButtonType.VUp:
                    self.VolumeUp()
                elif btnList[0].type == ButtonType.VDown:
                    self.VolumeDown()
                elif btnList[0].type == ButtonType.M1 \
                    or btnList[0].type == ButtonType.M2 \
                    or btnList[0].type == ButtonType.M3 \
                    or btnList[0].type == ButtonType.M4 :
                    self.PlayMemAlbum(btnList[0].type)

    def MemCurrentAlbum (self, btnType):
        if self.debug:
            print("-> Odioplayer: memorise current album and track"+str(self.currentAlbumId)+"-"+str(self.currentTrackId))

        if btnType == ButtonType.M1 \
            or btnType == ButtonType.M2 \
            or btnType == ButtonType.M3 \
            or btnType == ButtonType.M4 :
            memId= ButtonType.toString(btnType).lower()
            getattr(self.savedData, memId).albumId.string = str(self.currentAlbumId)
            getattr(self.savedData, memId).albumTitle.string = str(self.currentAlbumList[self.currentAlbumId])
            getattr(self.savedData, memId).trackId.string = str(self.currentTrackId)
            getattr(self.savedData, memId).trackTitle.string = str(self.currentTrackList[self.currentTrackId])
            self.SaveDataToFile()

    def SaveCurrentTrackPosition (self):
        #if self.debug:
        #    print("-> Odioplayer: save current track position ")

        self.currentTrackPosition = self.player.get_position()
        self.savedData.lastTrackPosition.string=str(self.currentTrackPosition)
        self.SaveDataToFile()

    def SaveCurrentAlbumAndTrack (self):
        if self.debug:
            print("-> Odioplayer: save current album and track")

        self.savedData.lastAlbumId.string=str(self.currentAlbumId)
        self.savedData.lastAlbumTitle.string=str(self.currentAlbumList[self.currentAlbumId])
        self.savedData.lastTrackId.string=str(self.currentTrackId)
        self.savedData.lastTrackTitle.string=str(self.currentTrackList[self.currentTrackId])
        self.SaveDataToFile()

    def SaveCurrentVolume (self):
        if self.debug:
            print("-> Odioplayer: save current volume")

        self.savedData.currentVolume.string = str(self.currentVolume)
        self.SaveDataToFile()

    def SaveDataToFile(self):
        os.system("sudo cp " + self.applicationPath + "/savedData.xml " + self.applicationPath + "/saveData.xml.orig")
        with open(self.savedDataFile.name,"r+") as f:
            f.seek(0)
            f.truncate()
            f.write(self.savedData.prettify())

    def ReInitSavedDataFile(self):
        with open(self.applicationPath+"/savedData.xml.orig") as origDataFile:
            self.savedData = BeautifulSoup(origDataFile,'xml')
            self.SaveDataToFile()

    def SetOutdoorVolume (self, value):
        if value:
            self.volumeMin = self.outdoorVolMin
            self.volumeMax = self.outdoorVolMax
            self.currentVolume = self.defaultOutdoorVol
            self.isSafeVolume = False
            self.player.audio_set_volume(self.currentVolume)

            if self.debug:
                print("-> Odioplayer: mode son extérieur activé")
        else:
            self.volumeMin = self.safeVolMin
            self.volumeMax = self.safeVolMax
            self.currentVolume = self.defaultSafeVol
            self.isSafeVolume = True
            self.player.audio_set_volume(self.currentVolume)

            if self.debug:
                print("-> Odioplayer: mode son intérieur activé")
        
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

        if not self.quiet:
            print("*** Albums ***")
            for subfolder in tmpList:
                print("-> "+subfolder)
            print("******")

        return tmpList

    def PlayAlbum(self, albumId, trackId=0, position=0):
        if self.player.is_playing():
            self.player.stop()

        self.currentAlbumId = albumId
        self.currentTrackId = trackId
        self.currentTrackPosition = position
        
        if self.debug or not self.quiet:
            print ("-> Odioplayer: play album - "+ self.currentAlbumList[self.currentAlbumId])

        self.currentAlbumPath = self.audioRoot+"/"+ self.currentAlbumList[self.currentAlbumId]
        self.currentTrackList = self.GetTrackList(self.currentAlbumPath)
        self.moduloTrackList = len(self.currentTrackList)

        self.PlayTrack(self.currentTrackId, self.currentTrackPosition)

    def PlayNextAlbum(self):
        if self.debug:
            print("-> Odioplayer: play next album")

        self.PlayAlbum((self.currentAlbumId +1)%self.moduloAlbumList)

    def PlayPreviousAlbum(self):
        if self.debug:
            print("-> Odioplayer: play previous album")

        self.PlayAlbum((self.currentAlbumId -1)%self.moduloAlbumList)

    def PlayMemAlbum(self, buttonType):
        memId= ButtonType.toString(buttonType).lower()
        if getattr(self.savedData, memId).albumId.string:
            tmpAlbumId = int(getattr(self.savedData, memId).albumId.string)
            tmpTrackId = int(getattr(self.savedData, memId).trackId.string)
            self.PlayAlbum(tmpAlbumId,tmpTrackId)
        else:
            if not self.quiet:
                print("-> Appuyez jusqu'au signal pour mémoriser l'album écouté")

    def GetTrackList(self, folder):
        tmpList = []
        for filename in os.listdir(folder):
            if filename.endswith(".mp3") or filename.endswith(".flac") or filename.endswith(".wav"):
                tmpList.append(filename)

        tmpList = sorted(tmpList)

        if not self.quiet:
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

    def AutoPlayNextTrack(self, event):
        self.playNextTrack = True

    def PlayTrack(self, trackId, position=0):

        if self.player.is_playing():
            self.player.stop()

        self.currentTrackId = trackId
        self.currentTrackPosition = position

        trackTitle  = self.GetTrackTitle(self.currentAlbumPath +"/"+ self.currentTrackList[self.currentTrackId])
        
        if (self.debug or not self.quiet) and trackTitle != None:
            print("-> Odioplayer: play track - " + trackTitle)

        self.currentMedia = self.vlcInstance.media_new(self.currentAlbumPath +"/"+ self.currentTrackList[self.currentTrackId])
        self.player.set_media(self.currentMedia)
        self.player.play()

        if self.currentTrackPosition and self.currentTrackPosition>0:
            if self.debug:
                print ("-> Odioplayer: start track at position - "+str(self.currentTrackPosition))
            self.player.set_position(self.currentTrackPosition)

        self.SaveCurrentAlbumAndTrack()

    def PlayNextTrack(self):
        self.PlayTrack((self.currentTrackId +1)%self.moduloTrackList)

    def PlayPreviousTrack(self):
        self.PlayTrack((self.currentTrackId -1)%self.moduloTrackList)

    def VolumeUp(self):
        if self.currentVolume + self.volumeIncr < self.volumeMax: 
            self.currentVolume = self.currentVolume + self.volumeIncr
        else: 
            self.currentVolume = self.volumeMax

        self.player.audio_set_volume(self.currentVolume)

        self.SaveCurrentVolume()

        if self.debug or not self.quiet:
            print ("-> Odioplayer: volume - "+str(self.player.audio_get_volume()))

    def VolumeDown(self):
        if self.currentVolume - self.volumeIncr > self.volumeMin: 
            self.currentVolume = self.currentVolume - self.volumeIncr
        else: 
            self.currentVolume = self.volumeMin

        self.player.audio_set_volume(self.currentVolume)

        self.SaveCurrentVolume()

        if self.debug or not self.quiet:
            print ("-> Odioplayer: volume - "+str(self.player.audio_get_volume()))

    def CheckButtonGPIO(self, out, in1, in2, in3):
        tmpBtList = []

        GPIO.setup(out, GPIO.OUT)

        GPIO.setup(in1, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        GPIO.setup(in2, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        GPIO.setup(in3, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

        GPIO.output(out, GPIO.HIGH)

        if GPIO.input(in1) == GPIO.HIGH:
            tmpBtList.extend(Button.FindButton(self.btnList,out,in1))

        if GPIO.input(in2) == GPIO.HIGH:
            tmpBtList.extend(Button.FindButton(self.btnList,out,in2))

        if GPIO.input(in3) == GPIO.HIGH:
            tmpBtList.extend(Button.FindButton(self.btnList,out,in3))

        return tmpBtList

def clearScrean():
    print("\033[H\033[J")

def main(argv):

   opts =None 
   args=None

   try:
      opts, args = getopt.getopt(argv,"qhi:o:",["ifile=","ofile="])
   except getopt.GetoptError:
      print ('usage:    Odioplayer2.py -q [--quiet] -i <inputfile> -o <outputfile>')

   for opt, arg in opts:
      if opt == '-h':
         print ('test.py -i <inputfile> -o <outputfile>')
         sys.exit()
      elif opt in ("-i", "--ifile"):
         print ('i mode activated')
      elif opt in ("-o", "--ofile"):
         print ('o mode activated')
      elif opt in ("-q", "--quiet"):
         print ('quiet mode activated')




if __name__ == "__main__":

    def shutdown():
        if debug:
            print("-> OdioPlayer: shutting down")

            #Todo clean stop player!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        if oPlayer.player.is_playing():
            oPlayer.player.pause()
            #oPlayer.player.stop()

        os.system("sudo sh /home/pi/stopSoundCard.sh")
        GPIO.cleanup()

    main(sys.argv[1:])

    debug=True
    quiet=True

    shutdownSoundFile='/home/pi/sound/smw_coin_reverse.wav'
    lipopiLogFile = "/home/pi/lipopi.log"
    sdGpio = 13
    lbGpio = 6

    oPlayer = None

    try:
        clearScrean()

        oPlayer = OdioPlayer(quiet, debug)
        
        sdm = ShutDownMgt(sdGpio, lbGpio, shutdown, shutdownSoundFile, lipopiLogFile, quiet, debug)

        oPlayer.Start()
    
    except ValueError:
        print ("ValueError:")
        print (ValueError)
        #theplayer.cleanup()