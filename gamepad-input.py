import argparse
import pyautogui
from enum import Enum
from hid_utils import HIDDeviceManager, DeviceMode, JoyConType, AxisType, ButtonType
from gamepad_input_helper import SoftwareKeyRepeatManager, DebugState
from gamepad_input_helper.out_events import OutEvent, DebugOut, KeyPress, KeyDown, KeyUp, TypeWrite, HotKey
from gamepad_input_helper.modes import LayerMode, JPInputMode, SymbolMode
import sys
import os
import yaml
import time
import asyncio
import functools
import threading
print = functools.partial(print, flush=True)

mode_names = [x.name for x in DeviceMode]

parser = argparse.ArgumentParser(description='gamepad input',
                                    formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument('-i','--vendor', type=lambda x: int(x,0), default=0x046d, help='vendor id')
parser.add_argument('-p','--product', type=lambda x: int(x,0), default=0xc216, help='product id')
parser.add_argument('-m','--device-mode', type=str, choices=mode_names,
                     default=DeviceMode.DINPUT.name, help='device mode')
parser.add_argument('-t','--threshold', type=float, default=0.5, help='axis threshold')
parser.add_argument('-s','--settings-file', type=str, default="settings.yaml", help='settings file')
parser.add_argument('-vv','--verbose', action='store_true', help='verbose')
parser.add_argument('-d','--debug', action='store_true', help='debug')
parser.add_argument('-de','--debug-event', action='store_true', help='debug events')
parser.add_argument('-da','--debug-axis', action='store_true', help='debug axis values')
parser.add_argument('-ds','--debug-states', action='store_true', help='debug button states')
parser.add_argument('-v','--version', action='version', version='%(prog)s 0.0.1', help='show version')
args = parser.parse_args()

vendor_id = args.vendor
product_id = args.product
device_mode = DeviceMode.from_str(args.device_mode)

is_debug = args.debug
is_verbose = args.verbose
DebugState.set_debug(is_debug)
DebugState.set_verbose(is_verbose)
axis_threshold = args.threshold

is_debug_event = args.debug_event
is_debug_axis = args.debug_axis
is_debug_states = args.debug_states

settings_file = args.settings_file

if is_debug:
    print(f"args: {args}")
    print(f"vendor_id from args: 0x{vendor_id:04x}")
    print(f"product_id from args: 0x{product_id:04x}")

_settings = yaml.safe_load(open(settings_file, 'r', encoding='utf-8'))

def get_setting_or(key: str, default: any):
    if key in _settings:
        return _settings[key]
    else:
        return default

if is_debug:
    print(f"settings: {_settings}")

# for device in hid.enumerate():
#     print(f"0x{device['vendor_id']:04x}:0x{device['product_id']:04x} {device['product_string']}")

manager = HIDDeviceManager()
gamepad = None
joycon_l = None
joycon_r = None

if device_mode == DeviceMode.JOYCON:
    vendor_id_l = 0x057e
    product_id_l = 0x2006
    vendor_id_r = 0x057e
    product_id_r = 0x2007

    print("[Info] on JOYCON mode, vendor and product id will be ignored", file=sys.stderr)

    for (vendor_id, product_id) in [(vendor_id_l, product_id_l), (vendor_id_r, product_id_r)]:
        if not manager.has_device(vendor_id, product_id):
            # print(f"[Error] device not found: 0x{vendor_id:04x}:0x{product_id:04x}", file=sys.stderr)
            if product_id == product_id_l:
                print(f"[Error] JOYCON_L device not found: 0x{vendor_id_l:04x}:0x{product_id_l:04x}", file=sys.stderr)
            else:
                print(f"[Error] JOYCON_R device not found: 0x{vendor_id_r:04x}:0x{product_id_r:04x}", file=sys.stderr)

            # current device list
            print("", file=sys.stderr)
            print("Current device list:", file=sys.stderr)
            manager.list_devices(out=sys.stderr)
            sys.exit(1)

        joycon_type = JoyConType.NONE

        if product_id == product_id_l:
            joycon_type = JoyConType.L
        else:
            joycon_type = JoyConType.R

        _gamepad = manager.get_device(vendor_id, product_id,
                                      mode=device_mode,
                                      joycon_type=joycon_type,
                                      axis_threshold=axis_threshold)
        if product_id == product_id_l:
            joycon_l = _gamepad
        else:
            joycon_r = _gamepad


    # raise NotImplementedError("JOYCON mode is not implemented yet")
else:

    if not manager.has_device(vendor_id, product_id):
        print(f"[Error] device not found: 0x{vendor_id:04x}:0x{product_id:04x}", file=sys.stderr)

        # current device list
        print("", file=sys.stderr)
        print("Current device list:", file=sys.stderr)
        manager.list_devices(out=sys.stderr)
        sys.exit(1)

    gamepad = manager.get_device(vendor_id, product_id, device_mode, axis_threshold=axis_threshold)

axis_value_dict: dict[AxisType, float] = {}
state_dict: dict[ButtonType, bool] = {}

software_key_repeat_enabled = get_setting_or('software_key_repeat_enabled', False)
software_key_repeat_delay_sec = get_setting_or('software_key_repeat_delay_sec', 0.1)
software_key_repeat_delay_sec_first = get_setting_or('software_key_repeat_delay_sec_first', 0.5)

softwareKeyRepeatManager = SoftwareKeyRepeatManager(
    delay_sec=software_key_repeat_delay_sec,
    delay_sec_first=software_key_repeat_delay_sec_first,
    enabled=software_key_repeat_enabled)

SoftwareKeyRepeatManager.set_singleton(softwareKeyRepeatManager)

if is_debug:
    print(f"softwareKeyRepeatManager: {softwareKeyRepeatManager}")

pyautogui.PAUSE = 0.005

layer = LayerMode.KEYBOARD_JP
jp_input_mode = JPInputMode.from_str(get_setting_or('jp_input_mode', "ROMAJI"))
symbol_mode = SymbolMode.DEFAULT

pre_ctrl_flag = False
pre_shift_flag = False
pre_star_flag = False
shift_press_started_time = None
star_press_started_time = None

out_events = []

def add_oev(ev: OutEvent):
    out_events.append(ev)

long_press_threshold_sec = get_setting_or('long_press_threshold_sec', 0.5)
use_ctrl_space_for_kanji_key = get_setting_or('use_ctrl_space_for_kanji_key', False)

is_shift_long_pressing = False
is_star_long_pressing = False

pressing_dict: dict[str, bool] = {}

def software_key_repeat_manager_thread():
    while True:
        softwareKeyRepeatManager.update()
        # t = time.time()
        time.sleep(0.001)
        # print(f"software_key_repeat_manager_thread: {time.time() - t} sec")

software_key_repeat_manager_thread = threading.Thread(target=software_key_repeat_manager_thread)
software_key_repeat_manager_thread.start()

try:
    while True:
        if device_mode == DeviceMode.JOYCON:
            l_events, l_raw = joycon_l.read_events_with_raw()
            r_events, r_raw = joycon_r.read_events_with_raw()

            if is_verbose:
                if l_raw:
                    l_raw_str = " ".join([f"{x:03d}" for x in l_raw])
                    print(f"JOYCON_L raw: {l_raw_str}")
                if r_raw:
                    r_raw_str = " ".join([f"{x:03d}" for x in r_raw])
                    print(f"JOYCON_R raw: {r_raw_str}")

            events = l_events + r_events
            axis_value_dict = joycon_l.get_axis_values() | joycon_r.get_axis_values()
            state_dict = joycon_l.get_states() | joycon_r.get_states()

            # for event in l_events:
            #     print(f"JOYCON_L {event}")
            # for event in r_events:
            #     print(f"JOYCON_R {event}")

        else:
            events, raw = gamepad.read_events_with_raw()
            axis_value_dict = gamepad.get_axis_values()
            state_dict = gamepad.get_states()
            if is_verbose:
                if raw:
                    # print(raw)
                    print(" ".join([f"{x:03d}" for x in raw]))

        if is_debug_event:
            for event in events:
                print(event)

        if is_debug_axis:
            for axis_type, value in axis_value_dict.items():
                print(f"{axis_type}: {value}")

        if is_debug_states:
            print("states:")
            print("-------")
            for button_type, value in state_dict.items():
                print(f"{button_type}: {value}")
            print("-------")

        if layer == LayerMode.KEYBOARD_JP:
            # Romaji mode
            if jp_input_mode == JPInputMode.ROMAJI:
                for event in events:
                    st = event.state
                    bt = event.button_type

                    # Shift button
                    if bt == ButtonType.ZL and st == True:
                        if not pre_shift_flag:
                            pre_shift_flag = True
                            shift_press_started_time = time.time()
                            add_oev(DebugOut("shift on"))
                        elif pre_shift_flag:
                            pre_shift_flag = False
                            shift_press_started_time = None
                            add_oev(DebugOut("shift off"))
                    elif bt == ButtonType.ZL and st == False:
                        if is_shift_long_pressing:
                            pre_shift_flag = False
                            shift_press_started_time = None
                            add_oev(DebugOut("shift off"))

                    # Star button
                    if bt == ButtonType.L and st == True:
                        if not pre_star_flag:
                            pre_star_flag = True
                            star_press_started_time = time.time()
                            add_oev(DebugOut("star on"))
                        elif pre_star_flag:
                            pre_star_flag = False
                            star_press_started_time = None
                            add_oev(DebugOut("star off"))

                    is_shift = pre_shift_flag or is_shift_long_pressing
                    is_star = pre_star_flag or is_star_long_pressing

                    if st == True:
                        if bt == ButtonType.A:
                            add_oev(KeyPress("a"))
                        elif bt == ButtonType.B:
                            add_oev(KeyPress("i"))
                        elif bt == ButtonType.X:
                            add_oev(KeyPress("e"))
                        elif bt == ButtonType.Y:
                            add_oev(KeyPress("o"))
                        elif bt == ButtonType.ANALOG_R_DOWN:
                            add_oev(KeyPress("x"))
                        elif bt == ButtonType.ANALOG_R_RIGHT:   
                            add_oev(TypeWrite("ya"))
                        elif bt == ButtonType.ANALOG_R_UP:
                            add_oev(TypeWrite("yu"))
                        elif bt == ButtonType.ANALOG_R_LEFT:
                            add_oev(TypeWrite("yo"))

                    if not is_shift and not is_star:
                        if st == True:
                            if bt == ButtonType.RIGHT:
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
                                add_oev(TypeWrite("xtsu"))
                            elif bt == ButtonType.SELECT:
                                pressing_dict["backspace"] = True
                                add_oev(KeyDown("backspace", repeat=True))
                            elif bt == ButtonType.START:
                                add_oev(KeyPress("enter"))
                            elif bt == ButtonType.ZR:
                                add_oev(KeyPress("u"))
                            elif bt == ButtonType.R:
                                add_oev(KeyPress("space"))
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
                            elif bt == ButtonType.ANALOG_L_RIGHT:
                                add_oev(TypeWrite("nn"))
                            elif bt == ButtonType.SELECT:
                                add_oev(KeyPress(","))
                            elif bt == ButtonType.START:
                                add_oev(KeyPress("."))
                            elif bt == ButtonType.ZR:
                                add_oev(KeyPress("p"))
                            elif bt == ButtonType.R:
                                add_oev(KeyPress("r"))
        
                    elif is_shift:
                        if st == True:
                            if bt == ButtonType.RIGHT:
                                add_oev(KeyPress("right"))
                            elif bt == ButtonType.DOWN:
                                add_oev(KeyPress("down"))
                            elif bt == ButtonType.LEFT:
                                add_oev(KeyPress("left"))
                            elif bt == ButtonType.UP:
                                add_oev(KeyPress("up"))
                            elif bt == ButtonType.SELECT:
                                add_oev(KeyPress("?"))
                            elif bt == ButtonType.START:
                                add_oev(KeyPress("!"))
                            elif bt == ButtonType.ZR:
                                add_oev(KeyPress("-"))
                            elif bt == ButtonType.R:
                                if use_ctrl_space_for_kanji_key:
                                    add_oev(HotKey("ctrl","space"))
                                else:
                                    add_oev(KeyPress("kanji"))
                                # add_oev(KeyPress("l"))

                    if st == False and bt == ButtonType.SELECT:
                        if "backspace" in pressing_dict and pressing_dict["backspace"]:
                            pressing_dict["backspace"] = False
                            add_oev(KeyUp("backspace"))

                    # Shift off when any button released
                    if not is_shift_long_pressing and pre_shift_flag:
                        if st == False and bt != ButtonType.ZL:
                            pre_shift_flag = False
                            shift_press_started_time = None
                            add_oev(DebugOut("shift off"))

                    # Star off when any button released
                    if not is_star_long_pressing and pre_star_flag:
                        if st == False and bt != ButtonType.L:
                            pre_star_flag = False
                            star_press_started_time = None
                            add_oev(DebugOut("star off"))

                # Shift long press
                prev_is_shift_long_pressing = is_shift_long_pressing
                is_shift_long_pressing = (
                    bool(ButtonType.ZL in state_dict and state_dict[ButtonType.ZL])
                    and (
                        shift_press_started_time is not None
                        and time.time() - shift_press_started_time > long_press_threshold_sec
                    )
                )

                if is_shift_long_pressing and not prev_is_shift_long_pressing:
                    add_oev(DebugOut("shift long press"))
            
            # Flick mode
            elif jp_input_mode == JPInputMode.FLICK:
                for event in events:
                    st = event.state
                    bt = event.button_type

                    if st == True and bt == ButtonType.R:
                        # flick center press button
                        
                        pass
        

        # end if: layer == Layer.KEYBOARD_JP

        for oev in out_events:
            if is_debug:
                print(f"{oev}")
            oev.execute()

        out_events.clear()

except KeyboardInterrupt:
    print("KeyboardInterrupt")
    # exit with killing all threads
    os._exit(1)