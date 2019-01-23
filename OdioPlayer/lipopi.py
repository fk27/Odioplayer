from os import system
from time import sleep
from time import strftime
from time import gmtime

import RPi.GPIO as GPIO


class ShutDownMgt(object):
    shutdown_pin = None
    shutdown_wait = 5
    low_battery_pin = None
    logfile = None
    logfile_path = None
    soundfile_path = None
    quiet = False
    debug = False
    shutdown = None

    def __init__(self, sdGpio, lbGpio, shutdown=None, soundfile=None, logfile=None, quiet=False, debug=False):

        if self.debug:
            print("-> lipopi: shutdown - init")

        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)

        self.shutdown_pin = sdGpio
        self.low_battery_pin = lbGpio
        self.shutdown = shutdown
        self.soundfile_path = soundfile
        self.logfile_path = logfile
        self.quiet = quiet
        self.debug = debug

        # setup the pin to check the shutdown switch - use the internal pull down resistor
        GPIO.setup(self.shutdown_pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

        # setup the low battery check pin
        GPIO.setup(self.low_battery_pin, GPIO.IN)

        # create a trigger for the shutdown switch and low battery pins
        GPIO.add_event_detect(self.shutdown_pin, GPIO.RISING, callback=self.lipopi_user_shutdown, bouncetime=100)
        GPIO.add_event_detect(self.low_battery_pin, GPIO.FALLING, callback=self.lipopi_low_battery_shutdown,
                              bouncetime=100)

        if self.debug:
            print("-> lipopi: shutdown - listening")

    def lipopi_user_shutdown(self, channel):
        if self.debug:
            print("-> lipopi: user shutdown")

        # self.shutdown()

        # if self.soundfile_path != None:
        #   system("sudo aplay "+ self.soundfile_path)

        if not self.quiet:
            system("sudo wall 'System shutting down in %d seconds'" % self.shutdown_wait)

        sleep(self.shutdown_wait)

        self.log(strftime("User Request - Shutting down at %a, %d %b %Y %H:%M:%S +0000\n", gmtime()))

    def lipopi_low_battery_shutdown(self, channel):
        if self.debug:
            print("-> lipopi: low battery shutdown")

        if self.soundfile_path is not None:
            system("sudo aplay " + self.soundfile_path)

        if not self.quiet:
            system("sudo wall 'System shutting down in %d seconds'" % self.shutdown_wait)

        sleep(self.shutdown_wait)

        self.log(strftime("Low Battery - Shutting down at %a, %d %b %Y %H:%M:%S +0000\n", gmtime()))

        self.shutdown()

    def log(self, msg):
        if self.logfile_path is not None:
            self.logfile = open(self.logfile_path, 'a+')
            self.logfile.write(msg)
            self.logfile.close()

    # def shut_down(self):

    #    self.before_shutdown()

    #    if self.debug:
    #        print("-> lipopi: shutting down - bye!")

    #    if self.logfile != None:
    #        self.logfile.close()

    #    #GPIO.cleanup()
    #    #os.system("sudo shutdown now")
