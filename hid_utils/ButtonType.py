from enum import Enum

class ButtonType(Enum):
    A = 0x01
    B = 0x02
    X = 0x04
    Y = 0x08
    L = 0x10
    R = 0x20
    ZL = 0x40
    ZR = 0x80
    START = 0x100
    SELECT = 0x200
    UP = 0x400
    DOWN = 0x800
    LEFT = 0x1000
    RIGHT = 0x2000
    # UP_LEFT = 0x4000
    # UP_RIGHT = 0x8000
    # DOWN_LEFT = 0x10000
    # DOWN_RIGHT = 0x20000
    ANALOG_L_UP = 0x40000
    ANALOG_L_DOWN = 0x80000
    ANALOG_L_LEFT = 0x100000
    ANALOG_L_RIGHT = 0x200000
    ANALOG_L_UP_LEFT = 0x400000
    ANALOG_L_UP_RIGHT = 0x800000
    ANALOG_L_DOWN_LEFT = 0x1000000
    ANALOG_L_DOWN_RIGHT = 0x2000000
    ANALOG_L_PRESS = 0x4000000
    ANALOG_R_UP = 0x8000000
    ANALOG_R_DOWN = 0x10000000
    ANALOG_R_LEFT = 0x20000000
    ANALOG_R_RIGHT = 0x40000000
    ANALOG_R_UP_LEFT = 0x80000000
    ANALOG_R_UP_RIGHT = 0x100000000
    ANALOG_R_DOWN_LEFT = 0x200000000
    ANALOG_R_DOWN_RIGHT = 0x400000000
    ANALOG_R_PRESS = 0x800000000