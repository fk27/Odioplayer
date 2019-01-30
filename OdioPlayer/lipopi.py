import os
from os import system
import time
from time import gmtime
from time import sleep
from time import strftime

import RPi.GPIO as GPIO


class ShutDownMgt(object):
    shutdown_pin = None
    shutdown_wait = None
    low_battery_pin = None
    logfile = None
    logfile_path = None
    quiet = False
    debug = False
    shutdown = None

    def __init__(self, sdGpio, lbGpio, logfile=None, quiet=False, debug=False, sdWait=None, sdFunction=None):

        if self.debug:
            print("-> lipopi: shutdown - init")

        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)

        self.shutdown_pin = sdGpio
        self.shutdown_wait = sdWait
        self.low_battery_pin = lbGpio
        self.shutdown = sdFunction
        self.logfile_path = logfile
        self.quiet = quiet
        self.debug = debug

        print("-> lipopi: logfile - " + self.logfile_path)
        self.log(strftime("Lipopi - init - at %a, %d %b %Y %H:%M:%S +0000\n", gmtime()))

        # setup the pin to check the shutdown switch - use the internal pull down resistor
        GPIO.setup(self.shutdown_pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

        # setup the low battery check pin
        GPIO.setup(self.low_battery_pin, GPIO.IN)

        # create a trigger for the shutdown switch and low battery pins
        GPIO.add_event_detect(self.shutdown_pin, GPIO.RISING, callback=self.lipopi_shutdown, bouncetime=4000)
        GPIO.add_event_detect(self.low_battery_pin, GPIO.FALLING, callback=self.lipopi_shutdown, bouncetime=100)

        # if GPIO.input(self.low_battery_pin):
        #     print('-> lipopi: low_battery_pin was HIGH')
        # else:
        #     print('-> lipopi: low_battery_pin was LOW')

        if self.debug:
            print("-> lipopi: shutdown - listening")

    def lipopi_shutdown(self, channel):
        print("-> lipopi_shutdown")
        origin = "Lipopi - "
        if channel == self.shutdown_pin:
            origin += "User Shutdown"
        elif channel == self.low_battery_pin:
            origin += "Low Battery Shutdown"

        self.log(strftime((origin + " - at %a, %d %b %Y %H:%M:%S +0000\n"), gmtime()))

        if self.debug:
            print("-> " + origin)

        # if self.shutdown is not None:
        #
        #     self.shutdown()
        #
        # elif self.shutdown_wait is not None:
        #
        #     if not self.quiet:
        #         system("sudo wall 'System shutting down in %d seconds'" % self.shutdown_wait)
        #
        #     sleep(self.shutdown_wait)
        #
        #     os.system("sudo shutdown now")
        #
        # else:
        #
        #     os.system("sudo shutdown now")

    def log(self, msg):
        print("-> lipopi ici1")
        if self.logfile_path is not None:
            print("-> lipopi ici2")
            self.logfile = open(self.logfile_path, 'a+')
            self.logfile.write(msg)
            self.logfile.close()


class ShutDownMgt2(object):
    shutdown_pin = None
    shutdown_wait = None
    low_battery_pin = None
    logfile = None
    logfile_path = None
    quiet = False
    debug = False
    shutdown = None

    shutdownBtnTime = None

    starttime = None

    def __init__(self, sdGpio, lbGpio, logfile=None, quiet=False, debug=False, sdPushDuration=0, sdWait=None, sdFunction=None):

        if self.debug:
            print("-> lipopi: shutdown - init")

        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)

        self.shutdown_pin = sdGpio
        self.shutdown_wait = sdWait
        self.low_battery_pin = lbGpio
        self.shutdown = sdFunction
        self.logfile_path = logfile
        self.quiet = quiet
        self.debug = debug

        # setup the pin to check the shutdown switch - use the internal pull down resistor
        GPIO.setup(self.shutdown_pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

        # setup the low battery check pin
        GPIO.setup(self.low_battery_pin, GPIO.IN)

        # create a trigger for the shutdown switch and low battery pins
        GPIO.add_event_detect(self.shutdown_pin, GPIO.BOTH, callback=self.lipopi_shutdown_btn_rising)

        GPIO.add_event_detect(self.low_battery_pin, GPIO.FALLING, callback=self.lipopi_shutdown, bouncetime=100)

        if self.debug:
            print("-> lipopi: shutdown - listening")

    def lipopi_shutdown_btn_rising(self, channel):
        if self.starttime is None:
            self.starttime = time.time()
            print("start:" + str(self.starttime))
        else:
            print("time:" + str(self.starttime-time.time()))

    def lipopi_shutdown(self, channel):

        origin = "Lipopi - "
        if channel == self.shutdown_pin:
            origin += "User Shutdown"
        elif channel == self.low_battery_pin:
            origin += "Low Battery Shutdown"

        self.log(strftime((origin + " - at %a, %d %b %Y %H:%M:%S +0000\n"), gmtime()))

        if self.debug:
            print("-> " + origin)

        if self.shutdown is not None:

            self.shutdown()

        elif self.shutdown_wait is not None:

            if not self.quiet:
                system("sudo wall 'System shutting down in %d seconds'" % self.shutdown_wait)

            sleep(self.shutdown_wait)

            os.system("sudo shutdown now")

        else:

            os.system("sudo shutdown now")

    def log(self, msg):
        if self.logfile_path is not None:
            self.logfile = open(self.logfile_path, 'a+')
            self.logfile.write(msg)
            self.logfile.close()


class ShutDownMgt3(object):
    shutdown_pin = None
    shutdown_wait = None
    low_battery_pin = None
    logfile = None
    logfile_path = None
    quiet = False
    debug = False
    shutdown = None

    def __init__(self, sdGpio, lbGpio, logfile=None, quiet=False, debug=False, sdWait=None, sdFunction=None):

        if self.debug:
            print("-> lipopi: shutdown - init")

        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)

        self.shutdown_pin = sdGpio
        self.shutdown_wait = sdWait
        self.low_battery_pin = lbGpio
        self.shutdown = sdFunction
        self.logfile_path = logfile
        self.quiet = quiet
        self.debug = debug
        self.stopping = False

        self.log(strftime("Lipopi - init - at %a, %d %b %Y %H:%M:%S +0000\n", gmtime()))

        # setup the pin to check the shutdown switch - use the internal pull down resistor
        GPIO.setup(self.shutdown_pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

        # setup the low battery check pin
        GPIO.setup(self.low_battery_pin, GPIO.IN)

        if self.debug:
            print("-> lipopi: shutdown - listening")

        while not self.stopping:
            if GPIO.input(self.low_battery_pin) == GPIO.LOW:
                self.lipopi_shutdown(self.low_battery_pin)

            if GPIO.input(self.shutdown_pin) == GPIO.HIGH:
                self.lipopi_shutdown(self.low_battery_pin)

            time.sleep(0.5)

    def lipopi_shutdown(self, channel):
        self.stopping = True

        origin = "Lipopi - "
        if channel == self.shutdown_pin:
            origin += "User Shutdown"
        elif channel == self.low_battery_pin:
            origin += "Low Battery Shutdown"

        self.log(strftime((origin + " - at %a, %d %b %Y %H:%M:%S +0000\n"), gmtime()))

        if self.debug:
            print("-> " + origin)

        # if self.shutdown is not None:
        #     self.shutdown()
        # elif self.shutdown_wait is not None:
        #     if not self.quiet:
        #         system("sudo wall 'System shutting down in %d seconds'" % self.shutdown_wait)
        #
        #     sleep(self.shutdown_wait)
        #     os.system("sudo shutdown now")
        # else:
        #     os.system("sudo shutdown now")

    def log(self, msg):
        if self.logfile_path is not None:
            self.logfile = open(self.logfile_path, 'a+')
            self.logfile.write(msg)
            self.logfile.close()
