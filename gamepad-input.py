import argparse
import hid
from enum import Enum
from hid_utils import HIDDeviceManager
import sys
import functools
print = functools.partial(print, flush=True)

# mode enum
class Mode(Enum):
    DINPUT = 1
    XINPUT = 2
    JOYCON = 3

parser = argparse.ArgumentParser(description='gamepad input',
                                    formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument('--vendor', type=lambda x: int(x,0), default=0x046d, help='vendor id')
parser.add_argument('--product', type=lambda x: int(x,0), default=0xc216, help='product id')
parser.add_argument('--mode', type=Mode, choices=list(Mode), default=Mode.DINPUT, help='mode')
args = parser.parse_args()

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

gamepad = manager.get_device(args.vendor, args.product)

while True:
    report = gamepad.read_raw(64)
    if report:
        print(report)