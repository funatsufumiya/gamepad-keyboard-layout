import pyautogui
import pygame

pygame.init()
pygame.joystick.init()

joystic_count = pygame.joystick.get_count()
print("Number of joysticks: {}".format(joystic_count))

if joystic_count == 0:
    quit()

joystick = pygame.joystick.Joystick(0)
joystick.init()

print("Joystick name: {}".format(joystick.get_name()))
print("Number of axes: {}".format(joystick.get_numaxes()))
print("Number of buttons: {}".format(joystick.get_numbuttons()))
print("Number of hats: {}".format(joystick.get_numhats()))

# print events
while True:
    for event in pygame.event.get():
        if event.type == pygame.JOYAXISMOTION:
            print("Joystick {} axis {} motion.".format(event.joy, event.axis))
        elif event.type == pygame.JOYBUTTONDOWN:
            print("Joystick {} button {} down.".format(event.joy, event.button))
        elif event.type == pygame.JOYBUTTONUP:
            print("Joystick {} button {} up.".format(event.joy, event.button))
        elif event.type == pygame.JOYHATMOTION:
            print("Joystick {} hat {} moved to {}.".format(event.joy, event.hat, event.value))