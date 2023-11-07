import sys
import os
import yaml
import time
# import asyncio
import threading
import argparse
import pyautogui
from enum import Enum

from hid_utils import HIDDeviceManager, DeviceMode, JoyConType, AxisType, ButtonType
from gamepad_input_helper import SoftwareKeyRepeatManager, DebugState, LayerModeState
from gamepad_input_helper.modes import LayerMode, JPInputMode, SymbolMode
from gamepad_input_helper.event_processor import OutEventManager, RomajiProcessor, FlickProcessor, AlphabetProcessor, EventProcessorManager

import functools
print = functools.partial(print, flush=True)

mode_names = [x.name for x in DeviceMode]

parser = argparse.ArgumentParser(description='gamepad input',
                                    formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument('-i','--vendor', type=lambda x: int(x,0), default=0x046d, help='vendor id')
parser.add_argument('-p','--product', type=lambda x: int(x,0), default=0xc216, help='product id')
parser.add_argument('-m','--device-mode', type=str, choices=mode_names,
                     default=DeviceMode.DINPUT.name, help='device mode')
# parser.add_argument('-t','--threshold', type=float, default=0.5, help='axis threshold')
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
# axis_threshold = args.threshold

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
    
axis_threshold = get_setting_or('axis_threshold', 0.3)

if is_debug:
    print(f"settings: {_settings}")

# for device in hid.enumerate():
#     print(f"0x{device['vendor_id']:04x}:0x{device['product_id']:04x} {device['product_string']}")

manager = HIDDeviceManager()
gamepad = None
joycon_l = None
joycon_r = None

# if DeviceMode.SWITCH_PRO
if device_mode == DeviceMode.SWITCH_PRO:
    vendor_id = 0x057e
    product_id = 0x2009

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

axis_dict: dict[AxisType, float] = {}
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

pyautogui.PAUSE = get_setting_or('pyautogui_pause_sec', 0.005)

layer_mode_state = LayerModeState(
    layer_mode = LayerMode.KEYBOARD_EN,
    # layer_mode = LayerMode.KEYBOARD_JP,
    # layer_mode = LayerMode.MOUSE,
    jp_input_mode = JPInputMode.from_str(get_setting_or('jp_input_mode', "ROMAJI")),
    symbol_mode = SymbolMode.DEFAULT)
LayerModeState.set_singleton(layer_mode_state)

long_press_threshold_sec = get_setting_or('long_press_threshold_sec', 0.5)
use_ctrl_space_for_kanji_key = get_setting_or('use_ctrl_space_for_kanji_key', False)
flick_axis_threshold = get_setting_or('flick_axis_threshold', 0.3)
flick_dakuten_double_backspace = get_setting_or('flick_dakuten_double_backspace', False)

out_event_manager = OutEventManager()
event_processor_manager = EventProcessorManager()
EventProcessorManager.set_singleton(event_processor_manager)

event_processor_manager.add_event_processor(
    RomajiProcessor(out_event_manager,
                    use_ctrl_space_for_kanji_key=use_ctrl_space_for_kanji_key,
                    long_press_threshold_sec=long_press_threshold_sec))

event_processor_manager.add_event_processor(
    AlphabetProcessor(out_event_manager,
                    use_ctrl_space_for_kanji_key=use_ctrl_space_for_kanji_key,
                    long_press_threshold_sec=long_press_threshold_sec))

event_processor_manager.add_event_processor(
    FlickProcessor(out_event_manager,
                    use_ctrl_space_for_kanji_key=use_ctrl_space_for_kanji_key,
                    long_press_threshold_sec=long_press_threshold_sec,
                    flick_axis_threshold=flick_axis_threshold,
                    flick_dakuten_double_backspace=flick_dakuten_double_backspace))

# jp_processor_type = RomajiProcessor if layer_mode_state.get_jp_input_mode() == JPInputMode.ROMAJI else FlickProcessor

# event_processor_manager.set_layer_mode_mappings({
#     LayerMode.KEYBOARD_JP: jp_processor_type,
#     LayerMode.KEYBOARD_EN: EnglishProcessor
# })

def software_key_repeat_manager_thread():
    while True:
        softwareKeyRepeatManager.update()
        # t = time.time()
        time.sleep(0.001)
        # print(f"software_key_repeat_manager_thread: {time.time() - t} sec")

software_key_repeat_manager_thread = threading.Thread(target=software_key_repeat_manager_thread)
software_key_repeat_manager_thread.start()

try:
    # Main loop
    while True:
        # JoyCon events
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
            axis_dict = joycon_l.get_axis_values() | joycon_r.get_axis_values()
            state_dict = joycon_l.get_states() | joycon_r.get_states()

            # for event in l_events:
            #     print(f"JOYCON_L {event}")
            # for event in r_events:
            #     print(f"JOYCON_R {event}")

        # Normal gamepad events
        else:
            events, raw = gamepad.read_events_with_raw()
            axis_dict = gamepad.get_axis_values()
            state_dict = gamepad.get_states()
            if is_verbose:
                if raw:
                    # print(raw)
                    print(" ".join([f"{x:03d}" for x in raw]))

        # Debugs

        if is_debug_event:
            for event in events:
                print(event)

        if is_debug_axis:
            for axis_type, value in axis_dict.items():
                print(f"{axis_type}: {value}")

        if is_debug_states:
            print("states:")
            print("-------")
            for button_type, value in state_dict.items():
                print(f"{button_type}: {value}")
            print("-------")

        # Process events
        # event_processor_manager.get_event_processor_by_layer_mode(layer_mode_state.get_layer_mode()).process(events, axis_dict, state_dict)

        if layer_mode_state.get_layer_mode() == LayerMode.KEYBOARD_JP:
            if layer_mode_state.get_jp_input_mode() == JPInputMode.ROMAJI:
                event_processor_manager.get_event_processor(RomajiProcessor).process(events, axis_dict, state_dict)
            elif layer_mode_state.get_jp_input_mode() == JPInputMode.FLICK:
                event_processor_manager.get_event_processor(FlickProcessor).process(events, axis_dict, state_dict)
            else:
                raise ValueError(f"Unknown JPInputMode: {layer_mode_state.get_jp_input_mode()}")
        else:
            event_processor_manager.get_event_processor(AlphabetProcessor).process(events, axis_dict, state_dict)

        out_event_manager.process_events()

except KeyboardInterrupt:
    print("KeyboardInterrupt")
    # exit with killing all threads
    os._exit(1)