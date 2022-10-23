from pygame import Surface, display as pg_display
from pygame import FULLSCREEN, SCALED
from pygame.time import Clock
from pygame.transform import scale

from scripts.utils import load_image


class DISPLAY:

    screen_size: tuple[int, int] = (640, 360)  # NO, YOU CAN'T MAKE A GAME THAT UGLY !!!!!1!
    screen: Surface = pg_display.set_mode(screen_size, FULLSCREEN | SCALED)  # 360p go brrrrrr

    GAME_NAME: str = "Untitled Game"
    pg_display.set_caption(GAME_NAME)
    pg_display.set_icon(load_image("icon.png"))

    CLOCK: Clock = Clock()
    FPS: int = 30
    FOV: float = 60.
    VIEW_DISTANCE: float = 6.5
    delta_time: float = 0.  # Time since the last frame in seconds

    @classmethod
    def update(cls):
        pg_display.update()
        cls.delta_time = cls.CLOCK.tick(cls.FPS) / 1000

    @classmethod
    def display(cls, surface: Surface):
        cls.screen.blit(surface, (0, 0))

    @classmethod
    def display_scaled(cls, surface: Surface):
        scale(surface, cls.screen_size, cls.screen)

