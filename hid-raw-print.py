import hid
import argparse
import functools
import sys
from hid_utils import HIDDeviceManager
print = functools.partial(print, flush=True)

def main():
    parser = argparse.ArgumentParser(description='print raw HID output',
                                        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('-i','--vendor', type=lambda x: int(x,0), default=0x057e, help='vendor id')
    parser.add_argument('-p','--product', type=lambda x: int(x,0), default=0x2006, help='product id')
    args = parser.parse_args()

    vendor_id = args.vendor
    product_id = args.product

    device_manager = HIDDeviceManager()

    if not device_manager.has_device(vendor_id, product_id):
        print(f"[Error] device not found: 0x{vendor_id:04x}:0x{product_id:04x}", file=sys.stderr)
        print("", file=sys.stderr)
        print("Current device list:", file=sys.stderr)
        device_manager.list_devices()
        sys.exit(1)

    device = device_manager.get_device(vendor_id, product_id)
    while True:
        raw = device.read_raw()
        if raw:
            # each 0-255 value print with empty padding to 3 digits
            print(" ".join([f"{x:03d}" for x in raw]))

if __name__ == "__main__":
    main()