from enum import Enum

class DeviceMode(Enum):
    DINPUT = 1
    XINPUT = 2
    JOYCON = 3
    SWITCH_PRO = 4

    @staticmethod
    def from_str(label):
        if label == "DINPUT":
            return DeviceMode.DINPUT
        elif label == "XINPUT":
            return DeviceMode.XINPUT
        elif label == "JOYCON":
            return DeviceMode.JOYCON
        elif label == "SWITCH_PRO":
            return DeviceMode.SWITCH_PRO
        else:
            raise ValueError(f"Unknown mode: {label}")