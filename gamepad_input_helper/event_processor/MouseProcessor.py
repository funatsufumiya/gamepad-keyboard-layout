import time
from .EventProcessor import EventProcessor
from ..out_events import OutEvent, DebugPrint, KeyPress, KeyDown, KeyUp, TypeWrite, HotKey, SetLayerMode, MouseClick, MouseWheel, MouseMoveRel, MouseButton
from hid_utils import ButtonEvent, AxisType, ButtonType
from ..modes import LayerMode

import functools
print = functools.partial(print, flush=True)

class MouseProcessor(EventProcessor):
    def __init__(self, out_event_manager,
            use_ctrl_space_for_kanji_key = False,
            long_press_threshold_sec = 0.5,
            mouse_axis_threshold = 0.5,
            mouse_move_speed_normal:float = 4.0,
            mouse_move_speed_slow:float = 2.0,
            mouse_move_speed_fast:float = 8.0,
            mouse_move_speed_very_slow:float = 1.0
        ):
        super().__init__(out_event_manager)
        self.pressing_dict: dict[str, bool] = {}
        self.pre_shift_flag = False
        self.shift_press_started_time = None
        self.is_shift_long_pressing = False
        self.prev_is_shift_long_pressing = False
        self.pre_star_flag = False
        self.star_press_started_time = None
        self.is_star_long_pressing = False
        self.prev_is_star_long_pressing = False

        self.use_ctrl_space_for_kanji_key = use_ctrl_space_for_kanji_key
        self.long_press_threshold_sec = long_press_threshold_sec
        self.mouse_axis_threshold = mouse_axis_threshold
        self.mouse_move_speed_normal = mouse_move_speed_normal
        self.mouse_move_speed_slow = mouse_move_speed_slow
        self.mouse_move_speed_fast = mouse_move_speed_fast
        self.mouse_move_speed_very_slow = mouse_move_speed_very_slow

        self.is_shift = False
        self.is_star = False

        self.prev_mouse_move_time = None

    def _mouse_process(self,
            axis_dict: dict[AxisType, float],
            state_dict: dict[ButtonType, bool]
        ):

        add_oev = self._add_out_event

        def axis_value(axis_type: AxisType) -> float:
            return axis_dict[axis_type] if axis_type in axis_dict else 0.5
        
        l_down_rate = axis_value(AxisType.ANALOG_L_DOWN)*2.0 - 1.0
        l_right_rate = axis_value(AxisType.ANALOG_L_RIGHT)*2.0 - 1.0
        r_down_rate = axis_value(AxisType.ANALOG_R_DOWN)*2.0 - 1.0
        r_right_rate = axis_value(AxisType.ANALOG_R_RIGHT)*2.0 - 1.0

        # print(f"l_v_rate {l_down_rate}, l_h_rate {l_right_rate}")
        # print(f"r_v_rate {r_down_rate}, r_h_rate {r_right_rate}")

        if not self.is_shift and not self.is_star:
            # normal mouse move (analog_r_stick)
            if self.prev_mouse_move_time is not None and time.time() - self.prev_mouse_move_time < 0.002:
                pass
            else:
                if abs(r_down_rate) > self.mouse_axis_threshold or abs(r_right_rate) > self.mouse_axis_threshold:
                    add_oev(MouseMoveRel(
                        int(r_right_rate * self.mouse_move_speed_normal),
                        int(r_down_rate * self.mouse_move_speed_normal)
                    ))
                    self.prev_mouse_move_time = time.time()
                    # print(f"mouse dx: {r_right_rate * self.mouse_move_speed_normal}, dy: {r_down_rate * self.mouse_move_speed_normal}")

            # slow mouse move (analog_l_stick)
            if self.prev_mouse_move_time is not None and time.time() - self.prev_mouse_move_time < 0.005:
                pass
            else:
                if abs(l_down_rate) > self.mouse_axis_threshold or abs(l_right_rate) > self.mouse_axis_threshold:
                    add_oev(MouseMoveRel(
                        int(l_right_rate * self.mouse_move_speed_slow),
                        int(l_down_rate * self.mouse_move_speed_slow)
                    ))
                    self.prev_mouse_move_time = time.time()
                    # print(f"mouse dx: {l_right_rate * self.mouse_move_speed_slow}, dy: {l_down_rate * self.mouse_move_speed_slow}")


        elif self.is_star:
            # fast mouse move (analog_r_stick)
            if self.prev_mouse_move_time is not None and time.time() - self.prev_mouse_move_time < 0.002:
                pass
            else:
                if abs(r_down_rate) > self.mouse_axis_threshold or abs(r_right_rate) > self.mouse_axis_threshold:
                    add_oev(MouseMoveRel(
                        int(r_right_rate * self.mouse_move_speed_fast),
                        int(r_down_rate * self.mouse_move_speed_fast)
                    ))
                    self.prev_mouse_move_time = time.time()
                    # print(f"mouse dx: {r_right_rate * self.mouse_move_speed_fast}, dy: {r_down_rate * self.mouse_move_speed_fast}")

            # very slow mouse move (analog_l_stick)
            if self.prev_mouse_move_time is not None and time.time() - self.prev_mouse_move_time < 0.005:
                pass
            else:
                if abs(l_down_rate) > self.mouse_axis_threshold or abs(l_right_rate) > self.mouse_axis_threshold:
                    add_oev(MouseMoveRel(
                        int(l_right_rate * self.mouse_move_speed_very_slow),
                        int(l_down_rate * self.mouse_move_speed_very_slow)
                    ))
                    self.prev_mouse_move_time = time.time()
                    # print(f"mouse dx: {l_right_rate * self.mouse_move_speed_very_slow}, dy: {l_down_rate * self.mouse_move_speed_very_slow}")


    def process(self,
            events: list[ButtonEvent],
            axis_dict: dict[AxisType, float],
            state_dict: dict[ButtonType, bool]
        ):

        add_oev = self._add_out_event

        def add_shift_oev(key: str) -> str:
            add_oev(KeyDown("shift"))
            add_oev(KeyPress(key))
            add_oev(KeyUp("shift"))

        for event in events:
            st = event.state
            bt = event.button_type

            # Shift button
            if bt == ButtonType.ZL and st == True:
                if not self.pre_shift_flag:
                    self.pre_shift_flag = True
                    self.shift_press_started_time = time.time()
                    add_oev(DebugPrint("shift on"))
                elif self.pre_shift_flag:
                    self.pre_shift_flag = False
                    self.shift_press_started_time = None
                    add_oev(DebugPrint("shift off"))
            elif bt == ButtonType.ZL and st == False:
                if self.is_shift_long_pressing:
                    self.pre_shift_flag = False
                    self.shift_press_started_time = None
                    add_oev(DebugPrint("shift off"))

            # Star button
            if bt == ButtonType.L and st == True:
                if not self.pre_star_flag:
                    self.pre_star_flag = True
                    self.star_press_started_time = time.time()
                    add_oev(DebugPrint("star on"))
                elif self.pre_star_flag:
                    self.pre_star_flag = False
                    self.star_press_started_time = None
                    add_oev(DebugPrint("star off"))
            elif bt == ButtonType.L and st == False:
                if self.is_star_long_pressing:
                    self.pre_star_flag = False
                    self.star_press_started_time = None
                    add_oev(DebugPrint("star off"))

            self.is_shift = self.pre_shift_flag or self.is_shift_long_pressing
            self.is_star = self.pre_star_flag or self.is_star_long_pressing

            if not self.is_shift and not self.is_star:
                if st == True:
                    if bt == ButtonType.SELECT:
                        self.pressing_dict["backspace"] = True
                        add_oev(KeyDown("backspace", repeat=True))
                    elif bt == ButtonType.START:
                        add_oev(KeyPress("enter"))
                    elif bt == ButtonType.ANALOG_R_PRESS:
                        add_oev(SetLayerMode(layer_mode=LayerMode.KEYBOARD_JP))
                    elif bt == ButtonType.R:
                        add_oev(MouseClick())
                    elif bt == ButtonType.ZR:
                        add_oev(MouseClick(MouseButton.RIGHT))

            elif self.is_shift and self.is_star:
                if st == True:
                    pass
            elif self.is_star:
                if st == True:
                    if bt == ButtonType.R:
                        add_oev(MouseClick())
                    elif bt == ButtonType.ZR:
                        add_oev(MouseClick(MouseButton.RIGHT))
            elif self.is_shift:
                if st == True:
                    pass

            if st == False and bt == ButtonType.SELECT:
                if "backspace" in self.pressing_dict and self.pressing_dict["backspace"]:
                    self.pressing_dict["backspace"] = False
                    add_oev(KeyUp("backspace"))

            # Shift off when any button released
            if not self.is_shift_long_pressing and self.pre_shift_flag:
                if st == False and bt != ButtonType.ZL:
                    self.pre_shift_flag = False
                    self.shift_press_started_time = None
                    add_oev(DebugPrint("shift off"))

            # Star off when any button released
            if not self.is_star_long_pressing and self.pre_star_flag:
                if st == False and bt != ButtonType.L:
                    self.pre_star_flag = False
                    self.star_press_started_time = None
                    add_oev(DebugPrint("star off"))

        self._mouse_process(axis_dict, state_dict)

        # Shift long press
        self.prev_is_shift_long_pressing = self.is_shift_long_pressing
        self.is_shift_long_pressing = (
            bool(ButtonType.ZL in state_dict and state_dict[ButtonType.ZL])
            and (
                self.shift_press_started_time is not None
                and time.time() - self.shift_press_started_time > self.long_press_threshold_sec
            )
        )
        if self.is_shift_long_pressing and not self.prev_is_shift_long_pressing:
            add_oev(DebugPrint("shift long press"))

        # Star long press
        self.prev_is_star_long_pressing = self.is_star_long_pressing
        self.is_star_long_pressing = (
            bool(ButtonType.L in state_dict and state_dict[ButtonType.L])
            and (
                self.star_press_started_time is not None
                and time.time() - self.star_press_started_time > self.long_press_threshold_sec
            )
        )
        if self.is_star_long_pressing and not self.prev_is_star_long_pressing:
            add_oev(DebugPrint("star long press"))

        
