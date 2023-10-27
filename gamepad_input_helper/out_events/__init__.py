import pyautogui
from ..SoftwareKeyRepeatManager import SoftwareKeyRepeatManager

class OutEvent:
    pass

class DebugOut(OutEvent):
    def __init__(self, msg: str):
        self.msg = msg

    def execute(self):
        pass

    def __str__(self):
        return f"Debug({self.msg})"
    

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
    def __init__(self, text: str, interval: float = 0.001):
        self.text = text
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