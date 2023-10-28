import time
import threading
import pyautogui
from .DebugState import DebugState
from .Singleton import Singleton

class SoftwareKeyRepeatManager(metaclass=Singleton):
    def __init__(self,
            delay_sec_first: float = 0.5,
            delay_sec: float = 0.1,
            enabled: bool = False):
        self.pressing_dict: dict[str, bool] = {}
        self.press_start_dict: dict[str, float] = {}
        self.repeat_started_dict: dict[str, bool] = {}
        self.delay_sec_first = delay_sec_first
        self.delay_sec = delay_sec
        self.enabled = enabled

    def set_delay_sec(self, delay_sec: float):
        self.delay_sec = delay_sec

    def set_enabled(self, enabled: bool):
        self.enabled = enabled

    def keyDown(self, key: str):
        self.pressing_dict[key] = True
        self.press_start_dict[key] = time.time_ns()
    
    def keyUp(self, key: str):
        if key in self.pressing_dict:
            del self.pressing_dict[key]
        
        if key in self.press_start_dict:
            del self.press_start_dict[key]

        if key in self.repeat_started_dict:
            del self.repeat_started_dict[key]

    def update(self):
        if not self.enabled:
            return 
        
        # supress RuntimeError: dictionary changed size during iteration
        pressing_dict_current = self.pressing_dict.copy()

        for key, is_pressing in pressing_dict_current.items():
            if is_pressing:
                delay_sec = self.delay_sec_first if key not in self.repeat_started_dict else self.delay_sec
                if key not in self.press_start_dict:
                    continue
                if time.time_ns() - self.press_start_dict[key] > delay_sec * 1e9:
                    def fn():
                        pyautogui.keyUp(key)
                        pyautogui.keyDown(key)
                    threading.Thread(target=fn).start()
                    self.repeat_started_dict[key] = True
                    self.press_start_dict[key] = time.time_ns()
                    if DebugState.is_debug():
                        print(f"soft key repeat: {key}")

    def __str__(self):
        return f"SoftwareKeyRepeatManager(delay_sec_first={self.delay_sec_first}, delay_sec={self.delay_sec}, enabled={self.enabled})"

    @staticmethod
    def get_singleton() -> 'SoftwareKeyRepeatManager':
        global softwareKeyRepeatManager
        if softwareKeyRepeatManager is None:
            raise RuntimeError("SoftwareKeyRepeatManager singleton is not initialized.")
        return softwareKeyRepeatManager
    
    @staticmethod
    def set_singleton(instance):
        global softwareKeyRepeatManager
        softwareKeyRepeatManager = instance