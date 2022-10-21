from enum import Enum, auto


from pygame import event as pg_event, QUIT


from scripts.display import DISPLAY
from scripts.input_handler import INPUT
from scripts.splash_screen import SPLASH_SCREEN


class GameState(Enum):
    SPLASH_SCREEN = auto()
    MAIN_MENU = auto()
    QUIT = auto()


class GAME:
    state: GameState = GameState.SPLASH_SCREEN

    @classmethod
    def events_handler(cls):
        for event in pg_event.get():
            if event.type == QUIT:
                cls.state = GameState.QUIT

    @classmethod
    def main(cls):
        while cls.state != GameState.QUIT:
            cls.events_handler()
            INPUT.update()

            match cls.state:
                case GameState.SPLASH_SCREEN:
                    if SPLASH_SCREEN.update():
                        cls.state = GameState.MAIN_MENU
                case GameState.MAIN_MENU:
                    ...

            DISPLAY.update()


