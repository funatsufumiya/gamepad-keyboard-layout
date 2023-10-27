import hid
import sys
from .DeviceMode import DeviceMode
from .ButtonEvent import ButtonEvent
from .ButtonType import ButtonType
from .JoyConType import JoyConType
import functools
print = functools.partial(print, flush=True)

class HIDDevice:
    button_state_dict: dict[ButtonType, bool] = {}

    def __init__(self, vendor_id, product_id,
                 mode=DeviceMode.DINPUT,
                 joycon_type=JoyConType.NONE,
                 axis_threshold=0.1, nonblocking=True):
        self.vendor_id = vendor_id
        self.product_id = product_id
        self.mode = mode
        self.axis_threshold = axis_threshold
        self.joycon_type = joycon_type
        self.nonblocking = nonblocking
        self.device = hid.device()
        self.device.open(self.vendor_id, self.product_id)
        self.device.set_nonblocking(self.nonblocking)

    def read_raw(self, size=64):
        return self.device.read(size)
    
    def _get_nbit(self, raw, offset_byte, offset_bit, nbit):
        byte = raw[offset_byte]
        return (byte >> offset_bit) & ((1 << nbit) - 1)
    
    def _read_states_dinput(self, raw: list[int]) -> list[ButtonEvent]:
        events: list[ButtonEvent] = []
        states: dict[ButtonType, bool] = {}

        # NOTE: raw[0] is ANALOG L left-right axis, left is 0x00, right is 0xff, center is 0x80
        # check using axis_threshold (percentage)
        states[ButtonType.ANALOG_L_LEFT] = bool(raw[0] < 0x80 - 0x80 * self.axis_threshold)
        states[ButtonType.ANALOG_L_RIGHT] = bool(raw[0] > 0x80 + 0x80 * self.axis_threshold)

        # NOTE: raw[1] is ANALOG L up-down axis, up is 0x00, down is 0xff, center is 0x80
        states[ButtonType.ANALOG_L_UP] = bool(raw[1] < 0x80 - 0x80 * self.axis_threshold)
        states[ButtonType.ANALOG_L_DOWN] = bool(raw[1] > 0x80 + 0x80 * self.axis_threshold)

        # NOTE: raw[2] is ANALOG R left-right axis, left is 0x00, right is 0xff, center is 0x80
        states[ButtonType.ANALOG_R_LEFT] = bool(raw[2] < 0x80 - 0x80 * self.axis_threshold)
        states[ButtonType.ANALOG_R_RIGHT] = bool(raw[2] > 0x80 + 0x80 * self.axis_threshold)

        # NOTE: raw[3] is ANALOG R up-down axis, up is 0x00, down is 0xff, center is 0x80
        states[ButtonType.ANALOG_R_UP] = bool(raw[3] < 0x80 - 0x80 * self.axis_threshold)
        states[ButtonType.ANALOG_R_DOWN] = bool(raw[3] > 0x80 + 0x80 * self.axis_threshold)

        # NOTE
        # raw[4] default value is 0x8
        # raw[4] 0 means UP
        # raw[4] 2 means RIGHT
        # raw[4] 4 means DOWN
        # raw[4] 6 means LEFT
        # raw[4] 1 means UP_RIGHT
        # raw[4] 3 means DOWN_RIGHT
        # raw[4] 5 means DOWN_LEFT
        # raw[4] 7 means UP_LEFT
        # raw[4] 24 means Y
        # raw[4] 40 means B
        # raw[4] 72 means A
        # raw[4] 136 means X
        # other combinations exists (ex: 200 means X + A, 70 means LEFT + A)

        arrow_bit = raw[4] & 0xf
        abxy_bit = raw[4] & 0xf0

        # print(f"abxy_bit: {abxy_bit}")
        # print(f"arrow_bit: {arrow_bit}")

        ## print raw[4] as binary
        # print(f"raw[4]: {raw[4]:08b}")

        states[ButtonType.Y] = bool(abxy_bit & 0x10)
        states[ButtonType.B] = bool(abxy_bit & 0x20)
        states[ButtonType.A] = bool(abxy_bit & 0x40)
        states[ButtonType.X] = bool(abxy_bit & 0x80)

        states[ButtonType.UP] = bool(arrow_bit == 0x00 or arrow_bit == 0x01 or arrow_bit == 0x07)
        states[ButtonType.RIGHT] = bool(arrow_bit == 0x01 or arrow_bit == 0x02 or arrow_bit == 0x03)
        states[ButtonType.DOWN] = bool(arrow_bit == 0x03 or arrow_bit == 0x04 or arrow_bit == 0x05)
        states[ButtonType.LEFT] = bool(arrow_bit == 0x05 or arrow_bit == 0x06 or arrow_bit == 0x07)


        states[ButtonType.L] = bool(raw[5] & 0x1)
        states[ButtonType.R] = bool(raw[5] & 0x2)
        states[ButtonType.ZL] = bool(raw[5] & 0x4)
        states[ButtonType.ZR] = bool(raw[5] & 0x8)
        states[ButtonType.ANALOG_L_PRESS] = bool(raw[5] & 0x40)
        states[ButtonType.ANALOG_R_PRESS] = bool(raw[5] & 0x80)

        states[ButtonType.SELECT] = bool(raw[5] & 0x10)
        states[ButtonType.START] = bool(raw[5] & 0x20)

        for button_type in states.keys():
            if not button_type in self.button_state_dict:
                if states[button_type] == True:
                    events.append(ButtonEvent(button_type, states[button_type]))
                    self.button_state_dict[button_type] = states[button_type]
            elif states[button_type] != self.button_state_dict[button_type]:
                events.append(ButtonEvent(button_type, states[button_type]))
                self.button_state_dict[button_type] = states[button_type]

        return events

    
    def _read_states_xinput(self, raw: list[int]) -> list[ButtonEvent]:
        raise NotImplementedError
    
    def _read_states_joycon_l(self, raw: list[int]) -> list[ButtonEvent]:
        events: list[ButtonEvent] = []
        states: dict[ButtonType, bool] = {}

        # raw[4] is button
        # 0: nothing pressed
        # 1: MINUS pressed
        # 8: ANALOG_L pressed
        # 32: CAPTURE pressed (ignore)

        states[ButtonType.SELECT] = bool(raw[4] & 0x1)
        states[ButtonType.ANALOG_L_PRESS] = bool(raw[4] & 0x8)

        # raw[5] is button
        # 0: nothing pressed
        # 1: DOWN pressed
        # 2: UP pressed
        # 4: RIGHT pressed
        # 8: LEFT pressed
        # 16: SR pressed (ignore)
        # 32: SL pressed (ignore)
        # 64: L pressed
        # 128: ZL pressed

        states[ButtonType.DOWN] = bool(raw[5] & 0x1)
        states[ButtonType.UP] = bool(raw[5] & 0x2)
        states[ButtonType.RIGHT] = bool(raw[5] & 0x4)
        states[ButtonType.LEFT] = bool(raw[5] & 0x8)
        states[ButtonType.L] = bool(raw[5] & 0x40)
        states[ButtonType.ZL] = bool(raw[5] & 0x80)

        left_horizontal = self._get_nbit(raw, 6, 0, 8) | (self._get_nbit(raw, 7, 0, 4) << 8)
        left_vertical = self._get_nbit(raw, 7, 4, 4) | (self._get_nbit(raw, 8, 0, 8) << 4)

        # print
        # print(f"left_horizontal: {left_horizontal}")
        # print(f"left_vertical: {left_vertical}")

        left_horizontal_max = 3329
        left_horizontal_min = 640
        left_horizontal_center = 1946
        left_vertical_max = 3389
        left_vertical_min = 1133
        left_vertical_center = 2172

        up_rate = (left_vertical - left_vertical_center) / (left_vertical_max - left_vertical_center)
        down_rate = (left_vertical_center - left_vertical) / (left_vertical_center - left_vertical_min)
        states[ButtonType.ANALOG_L_UP] = bool(up_rate > self.axis_threshold)
        states[ButtonType.ANALOG_L_DOWN] = bool(down_rate > self.axis_threshold)

        left_rate = (left_horizontal_center - left_horizontal) / (left_horizontal_center - left_horizontal_min)
        right_rate = (left_horizontal - left_horizontal_center) / (left_horizontal_max - left_horizontal_center)
        states[ButtonType.ANALOG_L_LEFT] = bool(left_rate > self.axis_threshold)
        states[ButtonType.ANALOG_L_RIGHT] = bool(right_rate > self.axis_threshold)

        # print rates
        # print(f"up_rate: {up_rate}")
        # print(f"down_rate: {down_rate}")

        for button_type in states.keys():
            if not button_type in self.button_state_dict:
                if states[button_type] == True:
                    events.append(ButtonEvent(button_type, states[button_type]))
                    self.button_state_dict[button_type] = states[button_type]
            elif states[button_type] != self.button_state_dict[button_type]:
                events.append(ButtonEvent(button_type, states[button_type]))
                self.button_state_dict[button_type] = states[button_type]

        return events

    def _read_states_joycon_r(self, raw: list[int]) -> list[ButtonEvent]:
        events: list[ButtonEvent] = []
        states: dict[ButtonType, bool] = {}

        # raw[3] is button
        # 0: nothing pressed
        # 1: Y pressed
        # 2: X pressed
        # 4: B pressed
        # 8: A pressed
        # 16: SR pressed (ignore)
        # 32: SL pressed (ignore)
        # 64: R pressed
        # 128: ZR pressed

        states[ButtonType.Y] = bool(raw[3] & 0x1)
        states[ButtonType.X] = bool(raw[3] & 0x2)
        states[ButtonType.B] = bool(raw[3] & 0x4)
        states[ButtonType.A] = bool(raw[3] & 0x8)
        states[ButtonType.R] = bool(raw[3] & 0x40)
        states[ButtonType.ZR] = bool(raw[3] & 0x80)

        # raw[4] is button
        # 0: nothing pressed
        # 2: PLUS pressed
        # 4: ANALOG_R pressed
        # 16: HOME pressed (ignore)

        states[ButtonType.START] = bool(raw[4] & 0x2)
        states[ButtonType.ANALOG_R_PRESS] = bool(raw[4] & 0x4)

        right_horizontal = self._get_nbit(raw, 9, 0, 8) | (self._get_nbit(raw, 10, 0, 4) << 8)
        right_vertical = self._get_nbit(raw, 10, 4, 4) | (self._get_nbit(raw, 11, 0, 8) << 4)

        # print
        # print(f"right_horizontal: {right_horizontal}")
        # print(f"right_vertical: {right_vertical}")

        right_horizontal_max = 3409
        right_horizontal_min = 838
        right_horizontal_center = 2100
        right_vertical_max = 2869
        right_vertical_min = 569
        right_vertical_center = 1805

        up_rate = (right_vertical - right_vertical_center) / (right_vertical_max - right_vertical_center)
        down_rate = (right_vertical_center - right_vertical) / (right_vertical_center - right_vertical_min)
        states[ButtonType.ANALOG_R_UP] = bool(up_rate > self.axis_threshold)
        states[ButtonType.ANALOG_R_DOWN] = bool(down_rate > self.axis_threshold)

        left_rate = (right_horizontal_center - right_horizontal) / (right_horizontal_center - right_horizontal_min)
        right_rate = (right_horizontal - right_horizontal_center) / (right_horizontal_max - right_horizontal_center)
        states[ButtonType.ANALOG_R_LEFT] = bool(left_rate > self.axis_threshold)
        states[ButtonType.ANALOG_R_RIGHT] = bool(right_rate > self.axis_threshold)
        
        # print rates
        # print(f"up_rate: {up_rate}")
        # print(f"down_rate: {down_rate}")
        # print(f"left_rate: {left_rate}")
        # print(f"right_rate: {right_rate}")

        for button_type in states.keys():
            if not button_type in self.button_state_dict:
                if states[button_type] == True:
                    events.append(ButtonEvent(button_type, states[button_type]))
                    self.button_state_dict[button_type] = states[button_type]
            elif states[button_type] != self.button_state_dict[button_type]:
                events.append(ButtonEvent(button_type, states[button_type]))
                self.button_state_dict[button_type] = states[button_type]

        return events
    
    def _read_states_joycon(self, raw: list[int]) -> list[ButtonEvent]:
        if self.joycon_type == JoyConType.L:
            return self._read_states_joycon_l(raw)
        elif self.joycon_type == JoyConType.R:
            return self._read_states_joycon_r(raw)
        elif self.joycon_type == JoyConType.NONE:
            raise RuntimeError("JoyConType is not specified")
        elif self.joycon_type == JoyConType.LR:
            raise RuntimeError("JoyConType.LR is not supported for HIDDevice.")
        else:
            raise RuntimeError(f"Unknown JoyConType: {self.joycon_type}")
        
    
    def _read_states_switch_pro(self, raw: list[int]) -> list[ButtonEvent]:
        raise NotImplementedError
    
    def read_events(self) -> list[ButtonEvent]:
        raw = self.read_raw()

        if not raw:
            return []

        if self.mode == DeviceMode.DINPUT:
            return self._read_states_dinput(raw)
        elif self.mode == DeviceMode.XINPUT:
            return self._read_states_xinput(raw)
        elif self.mode == DeviceMode.JOYCON:
            return self._read_states_joycon(raw)
        elif self.mode == DeviceMode.SWITCH_PRO:
            return self._read_states_switch_pro(raw)
        else:
            raise NotImplementedError(f"Unknown mode: {self.mode}")
        
    def read_events_with_raw(self) -> tuple[list[ButtonEvent], list[int]]:
        raw = self.read_raw()

        if not raw:
            return ([], None)

        if self.mode == DeviceMode.DINPUT:
            return (self._read_states_dinput(raw), raw)
        elif self.mode == DeviceMode.XINPUT:
            return (self._read_states_xinput(raw), raw)
        elif self.mode == DeviceMode.JOYCON:
            return (self._read_states_joycon(raw), raw)
        elif self.mode == DeviceMode.SWITCH_PRO:
            return (self._read_states_switch_pro(raw), raw)
        else:
            raise NotImplementedError(f"Unknown mode: {self.mode}")
        
    # def read_states(self) -> dict[ButtonType, bool]:
    #     self.read_events()
    #     return self.button_state_dict

    def get_states(self) -> dict[ButtonType, bool]:
        return self.button_state_dict
    
    def is_on(self, button_type: ButtonType) -> bool:
        return self.button_state_dict[button_type]