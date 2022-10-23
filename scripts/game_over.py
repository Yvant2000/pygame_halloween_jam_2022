from pygame import Surface
from pygame.mixer import stop as pg_mixer_stop

from scripts.display import DISPLAY
from scripts.text import TEXT
from scripts.input_handler import INPUT
from scripts.utils import load_image


class GAME_OVER_SCREEN:

    reason: str = ''
    alpha: int = 0

    screen: Surface = load_image("data", "main_menu", "game_over.png")

    @classmethod
    def reset(cls):
        pg_mixer_stop()
        cls.alpha = 0
        TEXT.replace(cls.reason, duration=25, fade_out=5, color=(50, 50, 50), size=8)

    @classmethod
    def update(cls) -> bool:

        black = Surface(DISPLAY.screen_size)
        black.fill((0, 0, 0))
        black.set_alpha((1 - cls.alpha) * 255)

        cls.alpha += DISPLAY.delta_time * 0.25

        DISPLAY.screen.blit(cls.screen, (0, 0))
        TEXT.update()
        DISPLAY.screen.blit(black, (0, 0))

        if cls.alpha >= 1:
            if INPUT.confirm():
                return True

        return False
