import argparse
import hid
from enum import Enum
from hid_utils import HIDDeviceManager, DeviceMode as Mode, JoyConType
import sys
import functools
print = functools.partial(print, flush=True)

mode_names = [x.name for x in Mode]

parser = argparse.ArgumentParser(description='gamepad input',
                                    formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument('-i','--vendor', type=lambda x: int(x,0), default=0x046d, help='vendor id')
parser.add_argument('-p','--product', type=lambda x: int(x,0), default=0xc216, help='product id')
parser.add_argument('-m','--mode', type=str, choices=mode_names,
                     default=Mode.DINPUT.name, help='mode')
parser.add_argument('-t','--threshold', type=float, default=0.3, help='axis threshold')
parser.add_argument('-vv','--verbose', action='store_true', help='verbose')
parser.add_argument('-v','--version', action='version', version='%(prog)s 0.0.1', help='show version')
args = parser.parse_args()

vendor_id = args.vendor
product_id = args.product
mode = Mode.from_str(args.mode)

is_verbose = args.verbose
axis_threshold = args.threshold

# for device in hid.enumerate():
#     print(f"0x{device['vendor_id']:04x}:0x{device['product_id']:04x} {device['product_string']}")

manager = HIDDeviceManager()
gamepad = None
joycon_l = None
joycon_r = None

if mode == Mode.JOYCON:
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
                                      mode=mode,
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

    gamepad = manager.get_device(vendor_id, product_id, mode, axis_threshold=axis_threshold)

while True:
    if mode == Mode.JOYCON:
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

        # for event in l_events:
        #     print(f"JOYCON_L {event}")
        # for event in r_events:
        #     print(f"JOYCON_R {event}")

    else:
        events, raw = gamepad.read_events_with_raw()
        if is_verbose:
            if raw:
                # print(raw)
                print(" ".join([f"{x:03d}" for x in raw]))

        for event in events:
            print(event)

    for event in events:
        print(event)