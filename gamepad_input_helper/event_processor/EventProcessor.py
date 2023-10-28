from .OutEventManager import OutEventManager
from hid_utils import ButtonEvent, AxisType, ButtonType

class EventProcessor():
    def __init__(self, out_event_manager: OutEventManager):
        self.out_event_manager = out_event_manager

    def process(self,
            events: list[ButtonEvent],
            axis_dict: dict[AxisType, float],
            state_dict: dict[ButtonType, bool]
        ):
        raise NotImplementedError()
    
    def _add_out_event(self, event):
        self.out_event_manager.add_event(event)