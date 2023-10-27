from .ButtonType import ButtonType

class ButtonEvent:
    def __init__(self, button_type: ButtonType, state: bool):
        self.button_type = button_type
        self.state = state

    def __str__(self):
        button_type_str = f"{self.button_type}"
        # remove ButtonType.
        button_type_str = button_type_str[button_type_str.find(".")+1:]
        return f"ButtonEvent({button_type_str}, {self.state})"