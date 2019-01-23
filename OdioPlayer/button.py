from buttontype import ButtonType



class Button(object):
    def __init__(self, gpioOut, gpioIn, t):
        self.gpioOut = gpioOut
        self.gpioIn = gpioIn
        self.type = t
        self.name = str(t)

    def __repr__(self):
        return "({0}-{1}) {2}".format(self.gpioOut, self.gpioIn, self.name)

    def __str__(self):
        return "({0}-{1}) {2}".format(self.gpioOut, self.gpioIn, self.name)

    @staticmethod
    def GetButtonListName(btnList):
        tmpBtPushedText = ''
        for bt in btnList:
            tmpBtPushedText = tmpBtPushedText + '[' + ButtonType.toString(bt.type) + ']'
        return tmpBtPushedText

    @staticmethod
    def FindButton(btnList, gpioOut, gpioIn):
        matches = (x for x in btnList if x.gpioIn == gpioIn and x.gpioOut == gpioOut)
        return list(matches)
