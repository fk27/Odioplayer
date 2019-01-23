import sys
import getopt
import RPi.GPIO as GPIO

from player import OdioPlayer
from lipopi import ShutDownMgt


def clearScrean():
    print("\033[H\033[J")


def main(argv):
    opts = None
    args = None

    try:
        opts, args = getopt.getopt(argv, "qhi:o:", ["ifile=", "ofile="])
    except getopt.GetoptError:
        print('usage:    Odioplayer2.py -q [--quiet] -i <inputfile> -o <outputfile>')

    for opt, arg in opts:
        if opt == '-h':
            print('test.py -i <inputfile> -o <outputfile>')
            sys.exit()
        elif opt in ("-i", "--ifile"):
            print('i mode activated')
        elif opt in ("-o", "--ofile"):
            print('o mode activated')
        elif opt in ("-q", "--quiet"):
            print('quiet mode activated')


if __name__ == "__main__":

    def shutdown():
        if debug:
            print("-> OdioPlayer: shutting down")

            # Todo clean stop player!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        oPlayer.shuttingDown = True

        if oPlayer.player.is_playing():
            oPlayer.player.pause()
            oPlayer.player.stop()

        if oPlayer.soundCardEnabled:
            oPlayer.soundCard.disable()

        GPIO.cleanup()


    main(sys.argv[1:])

    debug = True
    quiet = False

    shutdownSoundFile = '/home/pi/sounds/smw_coin_reverse.wav'
    lipopiLogFile = "/home/pi/log/lipopi.log"
    sdGpio = 13
    lbGpio = 6

    oPlayer = None

    try:
        clearScrean()

        oPlayer = OdioPlayer(quiet, debug)

        sdm = ShutDownMgt(sdGpio, lbGpio, shutdown, shutdownSoundFile, lipopiLogFile, quiet, debug)

        oPlayer.Start()

    except ValueError:
        print("ValueError:")
        print(ValueError)
        # theplayer.cleanup()
