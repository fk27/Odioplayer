import threading
import thread
import time

from espeak import espeak
from espeak import core as espeak_core

global isSpeaking
isSpeaking = False

def Speak(text):
    global isSpeaking

    while isSpeaking:
        print("waitting to speak")
        time.sleep(0.1)

    print("speaking")
    isSpeaking = True

    def Speak_Callback(event, pos, length):
        global isSpeaking
        if event == espeak_core.event_MSG_TERMINATED:
            isSpeaking = False
            print("speak finished")
            thread.exit()
            #if self.playerWasPlaying:
            #    #print("playerWasPlaying: " + str(self.currentTrackPosition))
            #    self.player.play()
            #    self.player.set_position(self.currentTrackPosition)
            #    self.playerWasPlaying = False

    espeak.set_voice("mb-fr1")
    espeak.set_parameter(espeak.Parameter.Rate,140)
    espeak.set_parameter(espeak.Parameter.Pitch,20)
    espeak.set_parameter(espeak.Parameter.Volume, 20)
       
    espeak.set_SynthCallback(Speak_Callback)
  
    call_result = espeak.synth(text)

thread.start_new_thread(Speak, ("hello hello hello hello hello hello hello hello hello hello hello monsieur le thread numero ",))

while isSpeaking:
    print("isSpeaking")

#id = 0
#while id<10:
#    print("active thread:"+str(threading.active_count()))
#    thread.start_new_thread(Speak, ("hello hello monsieur le thread numero "+str(id),))
#    id+=1
#    time.sleep(1)

#while threading.active_count()>0:
#    print("still active thread:"+str(threading.active_count()))




#class myThread (threading.Thread):
#   def __init__(self, threadID, name, counter):
#      threading.Thread.__init__(self)
#      self.threadID = threadID
#   def run(self):
#      print_name(self.threadID)

#def print_name(id):
#      print("thread " + str(id))
#      Speak("hello hello monsieur le thread numero "+str(id))
#      #Speak(str(id))

## Create new threads
#thread1 = myThread(1, "Thread-1", 1)
#thread2 = myThread(2, "Thread-2", 2)

## Start new Threads
#thread1.start()
#thread2.start()

#while 1:
#    thread1 = myThread(1, "Thread-1", 1)


#print "Exiting Main Thread"
