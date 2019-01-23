from enum import Enum


class ButtonType(Enum):
    Home = 1
    Left = 2
    Right = 3
    Up = 4
    Down = 5
    Play = 6
    VUp = 7
    VDown = 8
    M1 = 9
    M2 = 10
    M3 = 11
    M4 = 12

    def __int__(self):
        return self.value

    @classmethod
    def toString(cls, val):
        for k, v in vars(cls).items():
            if v == val:
                return k

    # @classmethod
    # def fromString(cls, str):
    #  return getattr(cls, str.upper(), None)
