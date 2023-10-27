from .ButtonType import ButtonType

class ButtonEvent:
    def __init__(self, button_type: ButtonType, state: bool):
        self.button_type = button_type
        self.state = state

    def __str__(self):
        return f"ButtonEvent({self.button_type}, {self.state})"