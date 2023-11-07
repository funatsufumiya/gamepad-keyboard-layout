import time
from enum import Enum

from .EventProcessor import EventProcessor
from ..out_events import OutEvent, DebugPrint, KeyPress, KeyDown, KeyUp, TypeWrite, HotKey
from hid_utils import ButtonEvent, AxisType, ButtonType

class FlickProcessor(EventProcessor):
    class FlickState(Enum):
        A = 1
        KA = 2
        SA = 3
        TA = 4
        NA = 5
        HA = 6
        MA = 7
        YA = 8
        RA = 9
        WA = 10
        SYMBOL = 11

    def __init__(self, out_event_manager,
            use_ctrl_space_for_kanji_key = False,
            long_press_threshold_sec = 0.5,
            flick_axis_threshold = 0.3,
            flick_dakuten_double_backspace = False
        ):
        super().__init__(out_event_manager)
        self.current_input_vowel = ""
        self.current_input_consonant = ""
        self.pressing_dict: dict[str, bool] = {}
        # self.pre_shift_flag = False
        # self.shift_press_started_time = None
        # self.is_shift_long_pressing = False
        # self.prev_is_shift_long_pressing = False
        self.pre_star_flag = False
        self.star_press_started_time = None
        self.is_star_long_pressing = False
        self.prev_is_star_long_pressing = False

        self.use_ctrl_space_for_kanji_key = use_ctrl_space_for_kanji_key
        self.long_press_threshold_sec = long_press_threshold_sec
        self.flick_axis_threshold = flick_axis_threshold
        self.flick_dakuten_double_backspace = flick_dakuten_double_backspace

    def get_flick_state(self, state_dict: dict[ButtonType, bool], axis_dict: dict[AxisType, float]) -> FlickState:
        def get_axis_value(axis_type: AxisType, _default_value=0.5):
            if axis_type not in axis_dict:
                return _default_value
            return axis_dict[axis_type]
        
        def get_value(axis_type: ButtonType):
            if axis_type not in state_dict:
                return False
            return state_dict[axis_type]
        
        is_hat_down = get_value(ButtonType.DOWN)
        is_hat_right = get_value(ButtonType.RIGHT)

        _c = 0.5

        # is_left = get_value(ButtonType.ANALOG_L_LEFT)
        # is_right = get_value(ButtonType.ANALOG_L_RIGHT)
        # is_up = get_value(ButtonType.ANALOG_L_UP)
        # is_down = get_value(ButtonType.ANALOG_L_DOWN)
        is_left = get_axis_value(AxisType.ANALOG_L_RIGHT) < _c - _c*self.flick_axis_threshold
        is_right = get_axis_value(AxisType.ANALOG_L_RIGHT) > _c + _c*self.flick_axis_threshold
        is_up = get_axis_value(AxisType.ANALOG_L_DOWN) < _c - _c*self.flick_axis_threshold
        is_down = get_axis_value(AxisType.ANALOG_L_DOWN) > _c + _c*self.flick_axis_threshold
        is_hori_center = not (is_left or is_right)
        is_vert_center = not (is_up or is_down)
        is_center = is_hori_center and is_vert_center

        if is_hat_down:
            return self.FlickState.WA
        elif is_hat_right:
            return self.FlickState.SYMBOL

        if is_center:
            return self.FlickState.NA
        elif is_left and is_up:
            return self.FlickState.A
        elif is_right and is_up:
            return self.FlickState.SA
        elif is_hori_center and is_up:
            return self.FlickState.KA
        elif is_left and is_vert_center:
            return self.FlickState.TA
        elif is_right and is_vert_center:
            return self.FlickState.HA
        elif is_left and is_down:
            return self.FlickState.MA
        elif is_right and is_down:
            return self.FlickState.RA
        elif is_hori_center and is_down:
            return self.FlickState.YA
        
        raise Exception("invalid flick state")

    def process(self,
            events: list[ButtonEvent],
            axis_dict: dict[AxisType, float],
            state_dict: dict[ButtonType, bool]
        ):

        add_oev = self._add_out_event
        FS = self.FlickState

        def set(v, c):
            self.current_input_vowel = v
            self.current_input_consonant = c

        for event in events:
            st = event.state
            bt = event.button_type
            fs = self.get_flick_state(state_dict, axis_dict)

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
            
            is_star = self.pre_star_flag or self.is_star_long_pressing

            if not is_star:
                if st == True:

                    if bt == ButtonType.Y or bt == ButtonType.SELECT:
                        self.pressing_dict["backspace"] = True
                        add_oev(KeyDown("backspace", repeat=True))
                        set("","")
                    elif bt == ButtonType.X:
                        # kanji
                        if self.use_ctrl_space_for_kanji_key:
                            add_oev(HotKey("ctrl", "space"))
                        else:
                            add_oev(KeyPress("kanji"))
                        set("","")

                    elif bt == ButtonType.B:
                        add_oev(KeyPress("space"))
                        set("","")

                    elif bt == ButtonType.A or bt == ButtonType.START:
                        add_oev(KeyPress("enter"))
                        set("","")

                    elif bt == ButtonType.LEFT:
                        # dakuten / komoji
                        def process_dakuten():
                            v = self.current_input_vowel
                            c = self.current_input_consonant

                            if c == "":
                                return
                            
                            nv = None

                            # special case
                            if v == "t" and c == "u":
                                nv = "xt"
                            elif v == "xt" and c == "u":
                                nv = "d"
                            elif v == "d" and c == "u":
                                nv = "t"
                            # dakuten
                            elif v == "k":
                                nv = "g"
                            elif v == "s":
                                nv = "z"
                            elif v == "t":
                                nv = "d"
                            elif v == "h":
                                nv = "b"
                            # komoji
                            elif v == "":
                                nv = "x"
                            elif v == "y":
                                nv = "xy"
                            # handakuten
                            elif v == "b":
                                nv = "p"
                            # back
                            elif v == "p":
                                nv = "h" 
                            elif v == "g":
                                nv = "k"
                            elif v == "z":
                                nv = "s"
                            elif v == "d":
                                nv = "t"
                            elif v == "b":
                                nv = "h"
                            elif v == "x":
                                nv = ""
                            elif v == "xy":
                                nv = "y"

                            if nv is None:
                                return
                            
                            self.current_input_vowel = nv
                            
                            if self.flick_dakuten_double_backspace:
                                add_oev(KeyPress("backspace"))
                                add_oev(KeyPress("backspace"))
                            else:
                                add_oev(KeyPress("backspace"))
                            add_oev(TypeWrite(nv+c))

                        process_dakuten()

                    elif bt == ButtonType.R:
                        # flick center press
                        
                        if fs == FS.A:
                            add_oev(KeyPress("a"))
                            set("","a")
                        elif fs == FS.KA:
                            add_oev(TypeWrite("ka"))
                            set("k","a")
                        elif fs == FS.SA:
                            add_oev(TypeWrite("sa"))
                            set("s","a")
                        elif fs == FS.TA:
                            add_oev(TypeWrite("ta"))
                            set("t","a")
                        elif fs == FS.NA:
                            add_oev(TypeWrite("na"))
                            set("n","a")
                        elif fs == FS.HA:
                            add_oev(TypeWrite("ha"))
                            set("h","a")
                        elif fs == FS.MA:
                            add_oev(TypeWrite("ma"))
                            set("m","a")
                        elif fs == FS.YA:
                            add_oev(TypeWrite("ya"))
                            set("y","a")
                        elif fs == FS.RA:
                            add_oev(TypeWrite("ra"))
                            set("r","a")
                        elif fs == FS.WA:
                            add_oev(TypeWrite("wa"))
                            set("w","a")
                        elif fs == FS.SYMBOL:
                            add_oev(KeyPress(","))
                            set("","")

                    elif bt == ButtonType.ANALOG_R_LEFT:
                        # flick left

                        if fs == FS.A:
                            add_oev(KeyPress("i"))
                            set("","i")
                        elif fs == FS.KA:
                            add_oev(TypeWrite("ki"))
                            set("k","i")
                        elif fs == FS.SA:
                            add_oev(TypeWrite("si"))
                            set("s","i")
                        elif fs == FS.TA:
                            add_oev(TypeWrite("ti"))
                            set("t","i")
                        elif fs == FS.NA:
                            add_oev(TypeWrite("ni"))
                            set("n","i")
                        elif fs == FS.HA:
                            add_oev(TypeWrite("hi"))
                            set("h","i")
                        elif fs == FS.MA:
                            add_oev(TypeWrite("mi"))
                            set("m","i")
                        elif fs == FS.YA:
                            add_oev(KeyPress("]")) # jis [
                            set("","")
                        elif fs == FS.RA:
                            add_oev(TypeWrite("ri"))
                            set("r","i")
                        elif fs == FS.WA:
                            add_oev(TypeWrite("wo"))
                            set("w","o")
                        elif fs == FS.SYMBOL:
                            add_oev(KeyPress("."))
                            set("","")

                    elif bt == ButtonType.ANALOG_R_UP:
                        # flick up

                        if fs == FS.A:
                            add_oev(KeyPress("u"))
                            set("","u")
                        elif fs == FS.KA:
                            add_oev(TypeWrite("ku"))
                            set("k","u")
                        elif fs == FS.SA:
                            add_oev(TypeWrite("su"))
                            set("s","u")
                        elif fs == FS.TA:
                            add_oev(TypeWrite("tu"))
                            set("t","u")
                        elif fs == FS.NA:
                            add_oev(TypeWrite("nu"))
                            set("n","u")
                        elif fs == FS.HA:
                            add_oev(TypeWrite("hu"))
                            set("h","u")
                        elif fs == FS.MA:
                            add_oev(TypeWrite("mu"))
                            set("m","u")
                        elif fs == FS.YA:
                            add_oev(TypeWrite("yu"))
                            set("y","u")
                        elif fs == FS.RA:
                            add_oev(TypeWrite("ru"))
                            set("r","u")
                        elif fs == FS.WA:
                            add_oev(TypeWrite("nn"))
                            set("n","n")
                        elif fs == FS.SYMBOL:
                            # add_oev(HotKey("shift","/")) # ?

                            # ?
                            add_oev(KeyDown("shift"))
                            add_oev(KeyPress("/")) 
                            add_oev(KeyUp("shift"))
                            set("","")

                    elif bt == ButtonType.ANALOG_R_RIGHT:
                        # flick right

                        if fs == FS.A:
                            add_oev(KeyPress("e"))
                            set("","e")
                        elif fs == FS.KA:
                            add_oev(TypeWrite("ke"))
                            set("k","e")
                        elif fs == FS.SA:
                            add_oev(TypeWrite("se"))
                            set("s","e")
                        elif fs == FS.TA:
                            add_oev(TypeWrite("te"))
                            set("t","e")
                        elif fs == FS.NA:
                            add_oev(TypeWrite("ne"))
                            set("n","e")
                        elif fs == FS.HA:
                            add_oev(TypeWrite("he"))
                            set("h","e")
                        elif fs == FS.MA:
                            add_oev(TypeWrite("me"))
                            set("m","e")
                        elif fs == FS.YA:
                            add_oev(KeyPress("\\")) # jis ]
                            set("","")
                        elif fs == FS.RA:
                            add_oev(TypeWrite("re"))
                            set("r","e")
                        elif fs == FS.WA:
                            add_oev(KeyPress("-"))
                            set("","")
                        elif fs == FS.SYMBOL:
                            # add_oev(HotKey("shift","1")) # !

                            # !
                            add_oev(KeyDown("shift"))
                            add_oev(KeyPress("1"))
                            add_oev(KeyUp("shift"))
                            set("","")

                    elif bt == ButtonType.ANALOG_R_DOWN:
                        # flick down

                        if fs == FS.A:
                            add_oev(KeyPress("o"))
                            set("","o")
                        elif fs == FS.KA:
                            add_oev(TypeWrite("ko"))
                            set("k","o")
                        elif fs == FS.SA:
                            add_oev(TypeWrite("so"))
                            set("s","o")
                        elif fs == FS.TA:
                            add_oev(TypeWrite("to"))
                            set("t","o")
                        elif fs == FS.NA:
                            add_oev(TypeWrite("no"))
                            set("n","o")
                        elif fs == FS.HA:
                            add_oev(TypeWrite("ho"))
                            set("h","o")
                        elif fs == FS.MA:
                            add_oev(TypeWrite("mo"))
                            set("m","o")
                        elif fs == FS.YA:
                            add_oev(TypeWrite("yo"))
                            set("y","o")
                        elif fs == FS.RA:
                            add_oev(TypeWrite("ro"))
                            set("r","o")
                        elif fs == FS.WA:
                            set("","")
                            # pass
                        elif fs == FS.SYMBOL:
                            set("","")
                            # pass

                else: # st == False
                    if bt == ButtonType.Y or bt == ButtonType.SELECT:
                        if "backspace" in self.pressing_dict and self.pressing_dict["backspace"]:
                            self.pressing_dict["backspace"] = False
                            add_oev(KeyUp("backspace"))

            else: # is_star == True
                if st == True:
                    if bt == ButtonType.RIGHT:
                        add_oev(KeyPress("right"))
                        set("","")
                    elif bt == ButtonType.DOWN:
                        add_oev(KeyPress("down"))
                        set("","")
                    elif bt == ButtonType.LEFT:
                        add_oev(KeyPress("left"))
                        set("","")
                    elif bt == ButtonType.UP:
                        add_oev(KeyPress("up"))
                        set("","")


            # Star off when any button released
            if not self.is_star_long_pressing and self.pre_star_flag:
                if st == False and bt != ButtonType.L:
                    self.pre_star_flag = False
                    self.star_press_started_time = None
                    add_oev(DebugPrint("star off"))

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