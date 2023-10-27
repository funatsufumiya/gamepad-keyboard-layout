import hid
import sys
import functools
from . import HIDDevice, DeviceMode as _DeviceMode
print = functools.partial(print, flush=True)

Mode = _DeviceMode.DeviceMode

class HIDDeviceManager:
    _devices = []

    def get_devices(self):
        if len(self._devices) == 0:
            self._update_devices()
        return self._devices
    
    def has_device(self, vendor_id, product_id):
        for device in self.get_devices():
            if device['vendor_id'] == vendor_id and device['product_id'] == product_id:
                return True
        return False
    
    def get_device(self, vendor_id, product_id, mode=Mode.DINPUT, nonblocking=True):
        if self.has_device(vendor_id, product_id):
            return HIDDevice.HIDDevice(vendor_id, product_id, mode, nonblocking)
        else:
            return None

    def _update_devices(self):
        self._devices = []

        dev_dict = {}

        for device in hid.enumerate():
            # if vendor_id is zero, or product_id is zero, or product_string is empty, skip
            if device['vendor_id'] == 0 or device['product_id'] == 0 or device['product_string'] == "":
                continue
            dev_dict[f"{device['vendor_id']:04x}:{device['product_id']:04x}"] = device

        # remove duplicates
        self._devices = list(dev_dict.values())

        # sort by vendor_id, product_id
        self._devices.sort(key=lambda x: (x['vendor_id'], x['product_id']))

    def list_devices(self, out=sys.stdout):
        print("[vendor_id]:[product_id] [product_string]")

        for device in self.get_devices():
            # if vendor_id is zero, or product_id is zero, or product_string is empty, skip
            if device['vendor_id'] == 0 or device['product_id'] == 0 or device['product_string'] == "":
                continue
            print(f"0x{device['vendor_id']:04x}:0x{device['product_id']:04x} {device['product_string']}", file=out)

if __name__ == "__main__":
    print("[Error] this file is a module", file=sys.stderr)