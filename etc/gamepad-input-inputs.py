import pyautogui
import inputs

devices = inputs.devices
# print(devices)

# get gamepads
gamepads = devices.gamepads
print("Number of gamepads: {}".format(len(gamepads)))

if len(gamepads) == 0:
    quit()

print(gamepads)

while True:
    events = inputs.get_gamepad()
    for event in events:
        print(event.ev_type, event.code, event.state)