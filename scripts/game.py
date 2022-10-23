from pygame import event as pg_event, QUIT

from scripts.display import DISPLAY
from scripts.input_handler import INPUT
from scripts.splash_screen import SPLASH_SCREEN
from scripts.main_menu import MAIN_MENU
from scripts.game_logic import GAME_LOGIC
from scripts.game_over import GAME_OVER_SCREEN
from scripts.utils import GameState


class GAME:
    state: GameState = GameState.SPLASH_SCREEN

    @classmethod
    def events_handler(cls):
        for event in pg_event.get():
            if event.type == QUIT:
                cls.state = GameState.QUIT

    @classmethod
    def main(cls):
        while True:
            cls.events_handler()
            INPUT.update()

            match cls.state:
                case GameState.SPLASH_SCREEN:
                    if SPLASH_SCREEN.update():
                        cls.state = GameState.MAIN_MENU

                case GameState.MAIN_MENU:
                    MAIN_MENU.update()

                case GameState.PLAYING:
                    GAME_LOGIC.update()

                case GameState.GAME_OVER:
                    if GAME_OVER_SCREEN.update():
                        cls.state = GameState.MAIN_MENU

                case GameState.QUIT:
                    break

            DISPLAY.update()
