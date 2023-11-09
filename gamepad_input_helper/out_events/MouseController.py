from .MouseButton import MouseButton
from pymouse import PyMouse

# singleton
class MouseController:
    @staticmethod
    def get_singleton():
        if not hasattr(MouseController, "singleton"):
            MouseController.singleton = MouseController()
        return MouseController.singleton
    
    def __init__(self):
        self.mouse = PyMouse()

    def move(self, x, y):
        self.mouse.move(x, y)

    def move_rel(self, dx, dy):
        (cx, cy) = self.mouse.position()
        self.mouse.move(cx + dx, cy + dy)
    
    def click(self, button: MouseButton = MouseButton.LEFT, count = 1, x: int | None = None, y: int | None = None):
        if x is None or y is None:
            (cx, cy) = self.mouse.position()
            self.mouse.click(cx, cy, int(button), count)
        else: 
            self.mouse.click(x, y, int(button), count)

    def scroll(self, x: int | None = None, y: int | None = None):
        self.mouse.scroll(horizontal=x, vertical=y)