import argparse
import hid
from enum import Enum
from hid_utils import HIDDeviceManager, DeviceMode as Mode
import sys
import functools
print = functools.partial(print, flush=True)

parser = argparse.ArgumentParser(description='gamepad input',
                                    formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument('-i','--vendor', type=lambda x: int(x,0), default=0x046d, help='vendor id')
parser.add_argument('-p','--product', type=lambda x: int(x,0), default=0xc216, help='product id')
parser.add_argument('-m','--mode', type=Mode, choices=list(Mode), default=Mode.DINPUT, help='mode')
parser.add_argument('-t','--threshold', type=float, default=0.3, help='axis threshold')
parser.add_argument('-vv','--verbose', action='store_true', help='verbose')
parser.add_argument('-v','--version', action='version', version='%(prog)s 0.0.1', help='show version')
args = parser.parse_args()

is_verbose = args.verbose
axis_threshold = args.threshold

# for device in hid.enumerate():
#     print(f"0x{device['vendor_id']:04x}:0x{device['product_id']:04x} {device['product_string']}")

manager = HIDDeviceManager()
if not manager.has_device(args.vendor, args.product):
    print(f"[Error] device not found: 0x{args.vendor:04x}:0x{args.product:04x}", file=sys.stderr)

    # current device list
    print("", file=sys.stderr)
    print("Current device list:", file=sys.stderr)
    manager.list_devices(out=sys.stderr)
    sys.exit(1)

gamepad = manager.get_device(args.vendor, args.product, args.mode, axis_threshold=axis_threshold)

while True:
    events, raw = gamepad.read_events_with_raw()
    if is_verbose:
        if raw:
            print(raw)

    for event in events:
        print(event)