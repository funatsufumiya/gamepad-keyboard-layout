import hid
import argparse
import functools
from hid_utils import HIDDeviceManager
print = functools.partial(print, flush=True)

def main():
    parser = argparse.ArgumentParser(description='show HID device list',
                                        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    args = parser.parse_args()

    device_manager = HIDDeviceManager()
    device_manager.list_devices()

if __name__ == "__main__":
    main()
    

