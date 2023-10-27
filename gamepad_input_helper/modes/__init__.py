from enum import Enum

class LayerMode(Enum):
    MOUSE = 1
    KEYBOARD_JP = 2
    KEYBOARD_EN = 3

class JPInputMode(Enum):
    ROMAJI = 0
    FLICK = 1

    @staticmethod
    def from_str(label):
        if label == "ROMAJI":
            return JPInputMode.ROMAJI
        elif label == "FLICK":
            return JPInputMode.FLICK
        else:
            raise ValueError(f"Unknown mode: {label}")

class SymbolMode(Enum):
    DEFAULT = 0