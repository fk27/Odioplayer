import RPi.GPIO as GPIO

class PAM8302A(object):

    debug = False
    sdGpio = None

    def __init__(self, sdGpio, debug=False):

        if self.debug:
            print("-> PAM8302A: init")

        self.sdGpio = sdGpio

        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.sdGpio, GPIO.OUT)

    def enable(self):
        if self.debug:
            print("-> PAM8302A: enable")

        GPIO.output(self.sdGpio, True)

    def disable(self):
        if self.debug:
            print("-> PAM8302A: disable")

        GPIO.output(self.sdGpio, False)

    def cleanup():
        if self.debug:
            print("-> PAM8302A: cleanup")

        GPIO.cleanup()

