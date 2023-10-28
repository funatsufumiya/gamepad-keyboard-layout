import pyautogui
from ..SoftwareKeyRepeatManager import SoftwareKeyRepeatManager
from ..modes import LayerMode, JPInputMode, SymbolMode
from ..LayerModeState import LayerModeState
from typing import Any

class OutEvent:
    pass

class DebugPrint(OutEvent):
    def __init__(self, msg: str):
        self.msg = msg

    def execute(self):
        pass

    def __str__(self):
        return f"DebugPrint({self.msg})"
    

class KeyPress(OutEvent):
    def __init__(self, key: str):
        self.key = key

    def execute(self):
        pyautogui.press(self.key)

    def __str__(self):
        return f"KeyPress({self.key})"

class KeyDown(OutEvent):
    def __init__(self, key: str, repeat: bool = False):
        self.key = key
        self.repeat = repeat

    def execute(self):
        pyautogui.keyDown(self.key)
        SoftwareKeyRepeatManager.get_singleton().keyDown(self.key)

    def __str__(self):
        return f"KeyDown({self.key}, repeat={self.repeat})"
    
class KeyUp(OutEvent):
    def __init__(self, key: str):
        self.key = key

    def execute(self):
        pyautogui.keyUp(self.key)
        SoftwareKeyRepeatManager.get_singleton().keyUp(self.key)

    def __str__(self):
        return f"KeyUp({self.key})"
    
class TypeWrite(OutEvent):
    def __init__(self, text: str, interval = None):
        self.text = text
        if interval is None:
            interval = pyautogui.PAUSE
        self.interval = interval

    def execute(self):
        pyautogui.typewrite(self.text, interval=self.interval)

    def __str__(self):
        return f"TypeWrite({self.text})"
    
class HotKey(OutEvent):
    def __init__(self, *args):
        self.args = args

    def execute(self):
        pyautogui.hotkey(*self.args)

    def __str__(self):
        return f"HotKey({self.args})"
    
class SetLayerMode(OutEvent):
    # def __init__(self, layer_mode: LayerMode, properties: dict = {str, Any}):
    def __init__(self, layer_mode: LayerMode):
        self.layer_mode = layer_mode
        # self.properties = properties

    def execute(self):
        layerModeState = LayerModeState.get_singleton()
        layerModeState.set_layer_mode(self.layer_mode)
        # layerModeState.set_layer_mode(self.layer_mode, self.properties)

    def __str__(self):
        return f"SetLayerMode({self.layer_mode})"