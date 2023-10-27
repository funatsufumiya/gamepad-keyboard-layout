import hid
import sys
from . import DeviceMode as _DeviceMode
import functools
print = functools.partial(print, flush=True)

DeviceMode = _DeviceMode.DeviceMode

class HIDDevice:
    def __init__(self, vendor_id, product_id, mode=DeviceMode.DINPUT, nonblocking=True):
        self.vendor_id = vendor_id
        self.product_id = product_id
        self.nonblocking = nonblocking
        self.device = hid.device()
        self.device.open(self.vendor_id, self.product_id)
        self.device.set_nonblocking(self.nonblocking)

    def read_raw(self, size):
        return self.device.read(size)