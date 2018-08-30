

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

def GetTrackList(folder):
    tmpList = []
    for filename in os.listdir(folder):
        if filename.endswith(".mp3") or filename.endswith(".flac") or filename.endswith(".wav"):
            tmpList.append(folder+'/'+filename)
            #MediaList.add_media(vlcInstance.media_new(audioRoot+'/'+filename))
            print (filename)
    return tmpList

audioRoot= '/home/pi/Music'
currentVolume = 50
volumeMin = 20
volumeMax = 80
volumeIncr = 5

currentFolder = audioRoot
currentTrackList = []
currentTrackId=0
lastTrackId=0

vlcInstance = vlc.Instance()
player = vlcInstance.media_player_new()

currentTrackList = GetTrackList(currentFolder)
moduloTrackList = len(currentTrackList)
currentMedia = vlcInstance.media_new(currentTrackList[0])
player.set_media(currentMedia)
player.audio_set_volume(volumeMin)





#def SongFinished(self, playNextSong):
#    print("SongFinished")
#    playNextSong[0] = True

#vlc_events.event_attach(vlc.EventType.MediaPlayerBackward.MediaPlayerEndReached, SongFinished, playNextSong)

#vlc_events = player.event_manager()

#SongFinished2(vlcInstance,player,currentTrackId,moduloTrackList)

#def SongFinished(self,vlcInstance,player,currentTrackId,moduloTrackList):
#    print("SongFinished " + str(vlcInstance)+" "+str(player)+ str(currentTrackId)+" "+str(moduloTrackList))
#    #currentTrackId = (currentTrackId +1)%moduloTrackList
#    #player.set_media(vlcInstance.media_new(currentTrackList[currentTrackId]))
#    #player.play()
     

#Ids = [currentTrackId, moduloTrackList]

#vlc_events = player.event_manager()

#def SongFinished2(self, vlcInstance, currentMedia, player, Ids, currentTrackList):
#    print("SongFinished2 ")
#    Ids[0] = (Ids[0] +1)%Ids[1]
#    currentMedia = vlcInstance.media_new(currentTrackList[Ids[0]])
#    player.set_media(currentMedia)
#    player.play()

#vlc_events.event_attach(vlc.EventType.MediaPlayerBackward.MediaPlayerEndReached, SongFinished2, vlcInstance, currentMedia, player , Ids, currentTrackList)


playNextSong = []
playNextSong.append(False)
vlc_events = player.event_manager()

def SongFinished2(self, playNextSong):
    print("SongFinished2 ")
    playNextSong[0] = True

vlc_events.event_attach(vlc.EventType.MediaPlayerBackward.MediaPlayerEndReached, SongFinished2, playNextSong)

def PlaySong(trackId):
    self.currentMedia = self.vlcInstance.media_new(self.currentTrackList[trackId])
    self.player.set_media(currentMedia)
    self.player.play()

def PlayNextSong():
    self.currentTrackId = (self.currentTrackId +1)%self.moduloTrackList
    self.PlaySong(self.currentTrackId)

def PlayPreviousSong():
    self.currentTrackId = (self.currentTrackId -1)%self.moduloTrackList
    self.PlaySong(self.currentTrackId)

def VolumeUp():
    tmpvol = player.audio_get_volume()
    if tmpvol + volumeIncr < volumeMax: 
        player.audio_set_volume(tmpvol+volumeIncr)
    else: 
        player.audio_set_volume(volumeMax)
    print(str(player.audio_get_volume()))

def VolumeDown():
    tmpvol=player.audio_get_volume()
    if tmpvol - volumeIncr > volumeMin: 
        player.audio_set_volume(tmpvol-volumeIncr)
    else: 
        player.audio_set_volume(volumeMin)
    print(str(player.audio_get_volume()))




import RPi.GPIO as GPIO
import time

from Button import Button
from ButtonType import ButtonType

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

        if playNextSong[0] == True:
            PlayNextSong()
            playNextSong[0] = False

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
                    PlayPreviousSong()
                elif buttonPushedList[0].type == ButtonType.Down:
                    PlayNextSong()
                #elif buttonPushedList[0].type == ButtonType.Left:
                #elif buttonPushedList[0].type == ButtonType.Right:
                elif buttonPushedList[0].type == ButtonType.VUp:
                    print("vup")
                elif buttonPushedList[0].type == ButtonType.VDown:
                    print("VDown")

        buttonPushedList = []

        time.sleep(0.2)
except:
    GPIO.cleanup()

GPIO.cleanup()