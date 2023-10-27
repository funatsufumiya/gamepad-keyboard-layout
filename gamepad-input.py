import hid

for device in hid.enumerate():
    print(f"0x{device['vendor_id']:04x}:0x{device['product_id']:04x} {device['product_string']}")

gamepad = hid.device()
gamepad.open(0x046d, 0xc216) # Logitech F310 Gamepad
# Joy-Con (L)
# gamepad.open(0x57e, 0x2006)
# Joy-Con (R)
# gamepad.open(0x57e, 0x2007)
gamepad.set_nonblocking(True)

while True:
    report = gamepad.read(64)
    if report:
        print(report)