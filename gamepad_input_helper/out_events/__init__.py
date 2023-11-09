import pyautogui
from ..SoftwareKeyRepeatManager import SoftwareKeyRepeatManager
from ..modes import LayerMode, JPInputMode, SymbolMode
from ..LayerModeState import LayerModeState
from .MouseController import MouseController
from .MouseButton import MouseButton
from typing import Any

# NOTE:
#
# - key control is handled with pyautogui
# - mouse control is handled with pymouse (PyUserInput)
#
# this is because pyautogui.PAUSE cause laggy mouse movement

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
    
class MouseMoveRel(OutEvent):
    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y

    def execute(self):
        mc = MouseController.get_singleton()
        mc.move_rel(self.x, self.y)
        # old_pause = None
        # if self.pause is False:
        #     old_pause = pyautogui.PAUSE
        #     pyautogui.PAUSE = 0
        # pyautogui.moveRel(xOffset=self.x, yOffset=self.y, duration=self.duration, _pause=self.pause)
        # if self.pause is False:
        #     pyautogui.PAUSE = old_pause

    def __str__(self):
        return f"MouseMove(x={self.x}, y={self.y})"
    
class MouseClick(OutEvent):
    def __init__(self, button: MouseButton = MouseButton.LEFT, count: int = 1):
        self.button = button
        self.count = count

    def execute(self):
        mc = MouseController.get_singleton()
        mc.click(button=self.button, count=self.count)
        # pyautogui.click(x=None, y=None, button=self.button)

    def __str__(self):
        return f"MouseClick(button={self.button}, count={self.count})"
    
class MouseWheel(OutEvent):
    def __init__(self, x: int = None, y: int = None):
        self.x = x
        self.y = y

    def execute(self):
        mc = MouseController.get_singleton()
        mc.scroll(x=self.x, y=self.y)
        # pyautogui.scroll(clicks=self.clicks, x=self.x, y=self.y, _pause=self.pause)

    def __str__(self):
        return f"MouseWheel(x={self.x}, y={self.y})"
    
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