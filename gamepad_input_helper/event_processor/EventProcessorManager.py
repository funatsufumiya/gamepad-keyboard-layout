from ..event_processor.EventProcessor import EventProcessor
from typing import Any
from ..modes import LayerMode

class EventProcessorManager:
    def __init__(self):
        self._event_processor_dict: dict[type[EventProcessor], EventProcessor] = {}
        self._layer_mode_mapping: dict['LayerMode', type[EventProcessor]] = {}

    def add_event_processor(self, event_processor):
        self._event_processor_dict[type(event_processor)] = event_processor

    def get_event_processor(self, event_processor_type: type[EventProcessor]):
        return self._event_processor_dict[event_processor_type]
    
    # def set_layer_mode_mapping(self, layer_mode: 'LayerMode', event_processor_type: type[EventProcessor]):
    #     self._layer_mode_mapping[layer_mode] = event_processor_type

    # def set_layer_mode_mappings(self, layer_mode_mapping: dict['LayerMode', type[EventProcessor]]):
    #     for layer_mode, event_processor_type in layer_mode_mapping.items():
    #         self.set_layer_mode_mapping(layer_mode, event_processor_type)

    # def get_layer_mode_mapping(self, layer_mode: 'LayerMode') -> type[EventProcessor] | None:
    #     if layer_mode not in self._layer_mode_mapping:
    #         return None
    #     return self._layer_mode_mapping[layer_mode]

    # def get_event_processor_by_layer_mode(self, layer_mode: 'LayerMode'):
    #     return self._event_processor_dict[self._layer_mode_mapping[layer_mode]]
    
    @staticmethod
    def get_singleton() -> 'EventProcessorManager':
        global eventProcessorManager
        if eventProcessorManager is None:
            raise RuntimeError("EventProcessorManager singleton is not initialized")
        return eventProcessorManager
    
    @staticmethod
    def set_singleton(instance):
        global eventProcessorManager
        eventProcessorManager = instance