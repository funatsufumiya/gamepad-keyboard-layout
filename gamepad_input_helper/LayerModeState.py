from .Singleton import Singleton
from .modes import LayerMode, JPInputMode, SymbolMode
# from .event_processor import EventProcessorManager
from typing import Any

class LayerModeState(metaclass=Singleton):
    def __init__(self,
        layer_mode = LayerMode.KEYBOARD_EN,
        jp_input_mode = JPInputMode.ROMAJI,
        symbol_mode = SymbolMode.DEFAULT):
        self._layer_mode = layer_mode
        self._jp_input_mode = jp_input_mode
        self._symbol_mode = symbol_mode

    def get_layer_mode(self):
        return self._layer_mode
    
    def get_jp_input_mode(self):
        return self._jp_input_mode
    
    def get_symbol_mode(self):
        return self._symbol_mode
    
    def set_layer_mode(self, layer_mode: LayerMode, properties: dict[str, Any] = {}):
        self._layer_mode = layer_mode
        from .event_processor import EventProcessorManager
        EventProcessorManager.get_singleton().get_event_processor_by_layer_mode(layer_mode).set_properties(properties)

    def set_jp_input_mode(self, jp_input_mode: JPInputMode):
        self._jp_input_mode = jp_input_mode

    def set_symbol_mode(self, symbol_mode: SymbolMode):
        self._symbol_mode = symbol_mode

    @staticmethod
    def set_singleton(instance):
        global layerModeState
        layerModeState = instance

    @staticmethod
    def get_singleton() -> 'LayerModeState':
        global layerModeState
        if layerModeState is None:
            raise RuntimeError("LayerModeState singleton is not initialized")
        return layerModeState
    