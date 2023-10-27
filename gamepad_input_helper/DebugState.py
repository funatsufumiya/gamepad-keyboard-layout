from .Singleton import Singleton

class _SingletonDebugState(metaclass=Singleton):
    def __init__(self):
        self._is_debug = False
        self._is_verbose = False
    
    def is_debug(self):
        return self._is_debug
    
    def is_verbose(self):
        return self._is_verbose
    
    def set_debug(self, is_debug):
        self._is_debug = is_debug
    
    def set_verbose(self, is_verbose):
        self._is_verbose = is_verbose

class DebugState:
    @staticmethod
    def is_debug():
        return _SingletonDebugState().is_debug()
    
    @staticmethod
    def is_verbose():
        return _SingletonDebugState().is_verbose()
    
    @staticmethod
    def set_debug(is_debug):
        _SingletonDebugState().set_debug(is_debug)

    @staticmethod
    def set_verbose(is_verbose):
        _SingletonDebugState().set_verbose(is_verbose)