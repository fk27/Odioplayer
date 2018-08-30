import os

isWidows = False

if os.name == 'nt':
    isWidows = True

if isWidows==False:
    from espeak import espeak
    espeak.set_voice("fr")
else:
    from subprocess import call


def speak( str ):
   if isWidows:
       os.system('espeak -vfr+f3 -s140 "'+str+'"')
       '''call(["espeak","-vfr+f3 -s140",str])'''
   else:
       espeak.synth(str)
   return

speak("Odio Player started.")


