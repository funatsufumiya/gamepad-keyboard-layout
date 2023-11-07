import time
from .EventProcessor import EventProcessor
from ..out_events import OutEvent, DebugPrint, KeyPress, KeyDown, KeyUp, TypeWrite, HotKey, SetLayerMode
from hid_utils import ButtonEvent, AxisType, ButtonType
from ..modes import LayerMode

class AlphabetProcessor(EventProcessor):
    def __init__(self, out_event_manager,
            use_ctrl_space_for_kanji_key = False,
            long_press_threshold_sec = 0.5
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

            is_shift = self.pre_shift_flag or self.is_shift_long_pressing
            is_star = self.pre_star_flag or self.is_star_long_pressing

            if not is_shift and not is_star:
                if st == True:
                    if bt == ButtonType.A:
                        add_oev(KeyPress("a"))
                    elif bt == ButtonType.B:
                        add_oev(KeyPress("i"))
                    elif bt == ButtonType.X:
                        add_oev(KeyPress("e"))
                    elif bt == ButtonType.Y:
                        add_oev(KeyPress("o"))
                    elif bt == ButtonType.RIGHT:
                        add_oev(KeyPress("k"))
                    elif bt == ButtonType.DOWN:
                        add_oev(KeyPress("s"))
                    elif bt == ButtonType.LEFT:
                        add_oev(KeyPress("t"))
                    elif bt == ButtonType.UP:
                        add_oev(KeyPress("h"))
                    elif bt == ButtonType.ANALOG_L_RIGHT:
                        add_oev(KeyPress("n"))
                    elif bt == ButtonType.ANALOG_L_DOWN:
                        add_oev(KeyPress("w"))
                    elif bt == ButtonType.ANALOG_L_LEFT:
                        add_oev(KeyPress("m"))
                    elif bt == ButtonType.ANALOG_L_UP:
                        add_oev(TypeWrite("y"))
                    elif bt == ButtonType.SELECT:
                        self.pressing_dict["backspace"] = True
                        add_oev(KeyDown("backspace", repeat=True))
                    elif bt == ButtonType.START:
                        add_oev(KeyPress("enter"))
                    elif bt == ButtonType.ZR:
                        add_oev(KeyPress("u"))
                    elif bt == ButtonType.R:
                        add_oev(KeyPress("space"))
                    elif bt == ButtonType.ANALOG_R_DOWN:
                        add_oev(KeyPress("c"))
                    elif bt == ButtonType.ANALOG_R_RIGHT:   
                        add_oev(KeyPress("l"))
                    elif bt == ButtonType.ANALOG_R_UP:
                        add_oev(KeyPress("p"))
                    elif bt == ButtonType.ANALOG_R_LEFT:
                        add_oev(KeyPress("r"))
                    elif bt == ButtonType.ANALOG_R_PRESS:
                        add_oev(SetLayerMode(layer_mode=LayerMode.MOUSE))
            elif is_shift and is_star:
                if st == True:
                    if bt == ButtonType.A:
                        add_oev(KeyPress("right"))
                    elif bt == ButtonType.B:
                        add_oev(KeyPress("down"))
                    elif bt == ButtonType.Y:
                        add_oev(KeyPress("left"))
                    elif bt == ButtonType.X:
                        add_oev(KeyPress("up"))
                    elif bt == ButtonType.SELECT:
                        add_oev(KeyPress("tab"))
                    elif bt == ButtonType.START:
                        add_oev(KeyPress("capslock"))
                    elif bt == ButtonType.ZR:
                        add_oev(KeyPress("esc"))
                    # large alphabet letters
                    elif bt == ButtonType.R:
                        add_oev(TypeWrite("Th"))
                    elif bt == ButtonType.RIGHT:
                        add_shift_oev("g")
                    elif bt == ButtonType.DOWN:
                        add_shift_oev("z")
                    elif bt == ButtonType.LEFT:
                        add_shift_oev("d")
                    elif bt == ButtonType.UP:
                        add_shift_oev("b")
                    elif bt == ButtonType.ANALOG_L_DOWN:
                        add_shift_oev("j")
                    elif bt == ButtonType.ANALOG_R_RIGHT:
                        add_shift_oev("f")
                    elif bt == ButtonType.ANALOG_R_UP:
                        add_shift_oev("v")
                    elif bt == ButtonType.ANALOG_R_LEFT:
                        add_shift_oev("x")
                    elif bt == ButtonType.ANALOG_R_DOWN:
                        add_shift_oev("q")
            elif is_star:
                if st == True:
                    if bt == ButtonType.RIGHT:
                        add_oev(KeyPress("g"))
                    elif bt == ButtonType.DOWN:
                        add_oev(KeyPress("z"))
                    elif bt == ButtonType.LEFT:
                        add_oev(KeyPress("d"))
                    elif bt == ButtonType.UP:
                        add_oev(KeyPress("b"))
                    elif bt == ButtonType.ANALOG_L_LEFT:
                        # !
                        add_oev(KeyDown("shift"))
                        add_oev(KeyPress("1"))
                        add_oev(KeyUp("shift"))
                    elif bt == ButtonType.ANALOG_L_UP:
                        # ?
                        add_oev(KeyDown("shift"))
                        add_oev(KeyPress("/")) 
                        add_oev(KeyUp("shift"))
                    elif bt == ButtonType.ANALOG_L_RIGHT:
                        add_oev(KeyPress("/"))
                    elif bt == ButtonType.ANALOG_L_DOWN:
                        add_oev(KeyPress("j"))
                    elif bt == ButtonType.SELECT:
                        add_oev(KeyPress(","))
                    elif bt == ButtonType.START:
                        add_oev(KeyPress("."))
                    elif bt == ButtonType.ZR:
                        add_oev(KeyPress("-"))
                    elif bt == ButtonType.R:
                        add_oev(TypeWrite("th"))
                    elif bt == ButtonType.ANALOG_R_DOWN:
                        add_oev(KeyPress("q"))
                    elif bt == ButtonType.ANALOG_R_RIGHT:   
                        add_oev(TypeWrite("f"))
                    elif bt == ButtonType.ANALOG_R_UP:
                        add_oev(TypeWrite("v"))
                    elif bt == ButtonType.ANALOG_R_LEFT:
                        add_oev(TypeWrite("x"))
            elif is_shift:
                if st == True:
                    if bt == ButtonType.R:
                        # kanji
                        if self.use_ctrl_space_for_kanji_key:
                            add_oev(HotKey("ctrl","space"))
                        else:
                            add_oev(KeyPress("kanji"))
                    # large alphabet letters
                    elif bt == ButtonType.RIGHT:
                        add_shift_oev("k")
                    elif bt == ButtonType.DOWN:
                        add_shift_oev("s")
                    elif bt == ButtonType.LEFT:
                        add_shift_oev("t")
                    elif bt == ButtonType.UP:
                        add_shift_oev("h")
                    elif bt == ButtonType.A:
                        add_shift_oev("a")
                    elif bt == ButtonType.B:
                        add_shift_oev("i")
                    elif bt == ButtonType.X:
                        add_shift_oev("e")
                    elif bt == ButtonType.Y:
                        add_shift_oev("o")
                    elif bt == ButtonType.ZR:
                        add_shift_oev("u")
                    elif bt == ButtonType.SELECT:
                        # '
                        add_oev(KeyDown("shift"))
                        add_oev(KeyPress("7"))
                        add_oev(KeyUp("shift"))
                    elif bt == ButtonType.START:
                        # "
                        add_oev(KeyDown("shift"))
                        add_oev(KeyPress("2"))
                        add_oev(KeyUp("shift"))
                    elif bt == ButtonType.ANALOG_L_DOWN:
                        add_shift_oev("w")
                    elif bt == ButtonType.ANALOG_L_RIGHT:
                        add_shift_oev("n")
                    elif bt == ButtonType.ANALOG_L_UP:
                        add_shift_oev("y")
                    elif bt == ButtonType.ANALOG_L_LEFT:
                        add_shift_oev("m")
                    elif bt == ButtonType.ANALOG_R_DOWN:
                        add_shift_oev("c")
                    elif bt == ButtonType.ANALOG_R_RIGHT:
                        add_shift_oev("l")
                    elif bt == ButtonType.ANALOG_R_UP:
                        add_shift_oev("p")
                    elif bt == ButtonType.ANALOG_R_LEFT:
                        add_shift_oev("r")

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

        
