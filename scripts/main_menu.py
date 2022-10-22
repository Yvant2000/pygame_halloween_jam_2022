
from pygame import Surface

from scripts.utils import load_image
from scripts.display import DISPLAY
from scripts.input_handler import INPUT


class Button:
    def __init__(self, name: str, x: int, y: int):
        self.surface: Surface = load_image("data", "main_menu", f"{name}.png")
        self.surface_selected: Surface = load_image("data", "main_menu", f"{name}_selected.png")
        self.width, self.height = self.surface.get_size()
        self.pos = (x, y)

    def get_image(self, selected: bool):
        return self.surface_selected if selected else self.surface


# noinspection PyClassHasNoInit
class MAIN_MENU:
    background_image: Surface = load_image("data", "main_menu", "background.png")
    selected_button: int = 0

    BUTTONS: list[Button] = [
        Button("play", 243, 116),
        Button("endless", 243, 185),
        Button("quit", 243, 260)
    ]

    pressing: bool = False

    @classmethod
    def update(cls) -> None:
        DISPLAY.display(cls.background_image)

        for i, button in enumerate(cls.BUTTONS):
            DISPLAY.screen.blit(
                button.get_image(cls.selected_button == i),
                button.pos
            )

        if INPUT.up():
            cls.selected_button = (selected_button - 1) % len(cls.BUTTONS)

