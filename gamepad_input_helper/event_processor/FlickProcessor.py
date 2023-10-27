import time
from .EventProcessor import EventProcessor
from ..out_events import OutEvent, DebugOut, KeyPress, KeyDown, KeyUp, TypeWrite, HotKey
from hid_utils import ButtonEvent, AxisType, ButtonType

class FlickProcessor(EventProcessor):
    def __init__(self, out_event_manager,
            use_ctrl_space_for_kanji_key = False,
            long_press_threshold_sec = 0.5
        ):
        super().__init__(out_event_manager)
        # self.pressing_dict: dict[str, bool] = {}
        # self.pre_shift_flag = False
        # self.shift_press_started_time = None
        # self.is_shift_long_pressing = False
        # self.prev_is_shift_long_pressing = False
        # self.pre_star_flag = False
        # self.star_press_started_time = None
        # self.is_star_long_pressing = False
        # self.prev_is_star_long_pressing = False

        self.use_ctrl_space_for_kanji_key = use_ctrl_space_for_kanji_key
        self.long_press_threshold_sec = long_press_threshold_sec

    def process(self,
            events: list[ButtonEvent],
            axis_value_dict: dict[AxisType, float],
            state_dict: dict[ButtonType, bool]
        ):

        add_oev = self._add_out_event

        for event in events:
            st = event.state
            bt = event.button_type

            if st == True and bt == ButtonType.R:
                # flick center press button
                
                pass