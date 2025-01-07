from collections import namedtuple
from enum import StrEnum, IntEnum

Resolution = namedtuple("Resolution", "width height")


class Rotation(IntEnum):
    ROTATE_0 = 0
    ROTATE_90 = 90
    ROTATE_180 = 180
    ROTATE_270 = 270


class Resize(StrEnum):
    FIT = 'FIT'
    STRETCH = 'STRETCH'
    CROP = 'CROP'
    NONE = 'NONE'


class BackgroundColour(StrEnum):
    BLACK = 'BLACK'
    WHITE = 'WHITE'


class Mode(StrEnum):
    FAST = 'FAST'
    PARTIAL = 'PARTIAL'
    FOUR_GRAY = '4GRAY'
