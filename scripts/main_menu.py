
from pygame import Surface
from pygame.mixer import Sound

from scripts.display import DISPLAY
from scripts.input_handler import INPUT
from scripts.visuals import VISUALS
from scripts.utils import load_image, GameState, join_path


class Button:
    def __init__(self, name: str, x: int, y: int):
        self.surface: Surface = load_image("data", "main_menu", f"{name}.png")
        self.surface_selected: Surface = load_image("data", "main_menu", f"{name}_selected.png")
        self.width, self.height = self.surface.get_size()
        self.pos = (x, y)

    def get_image(self, selected: bool):
        return self.surface_selected if selected else self.surface


class MAIN_MENU:
    background_image: Surface = load_image("data", "main_menu", "background.png")
    selected_button: int = 0

    pressing_up: bool = False
    pressing_down: bool = False

    main_game_beaten: bool = False
    endless_mode_score: int = 0

    BUTTONS: list[Button] = [
        Button("play", 243, 116),
        Button("endless", 243, 185) if main_game_beaten else Button("endless_blocked", 243, 185),
        Button("quit", 243, 260)
    ]

    white_noise: Sound = Sound(join_path("data", "sounds", "sfx", "white_noise_hit.ogg"))

    @classmethod
    def update(cls) -> None:
        DISPLAY.display(cls.background_image)

        for i, button in enumerate(cls.BUTTONS):
            DISPLAY.screen.blit(
                button.get_image(cls.selected_button == i),
                button.pos
            )

        if INPUT.confirm():
            from scripts.game import GAME
            from scripts.game_logic import GAME_LOGIC
            match cls.selected_button:
                case 0:
                    GAME_LOGIC.reset()
                    GAME.state = GameState.PLAYING
                case 1:
                    if not cls.main_game_beaten:
                        if cls.white_noise.get_num_channels() < 1:
                            VISUALS.fried = 1.0
                            cls.white_noise.play()
                        return
                    raise NotImplementedError  # TODO: Implement endless mode
                case 2:  # QUIT BUTTON
                    GAME.state = GameState.QUIT

        elif INPUT.up():
            if not cls.pressing_up:
                cls.selected_button = (cls.selected_button - 1) % len(cls.BUTTONS)
                cls.pressing_up = True
        else:
            cls.pressing_up = False

            if INPUT.down():
                if not cls.pressing_down:
                    cls.selected_button = (cls.selected_button + 1) % len(cls.BUTTONS)
                    cls.pressing_down = True
            else:
                cls.pressing_down = False

        VISUALS.display()


try:
    with open("save.txt", "r") as file:
        content = file.read().split("\n")
        MAIN_MENU.main_game_beaten = content[0] == "True"
        MAIN_MENU.endless_mode_score = int(content[1])
except FileNotFoundError:
    pass
