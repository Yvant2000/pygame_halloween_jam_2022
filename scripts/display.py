

from pygame import Surface, display as pg_display
from pygame import FULLSCREEN, SCALED
from pygame.time import Clock
from pygame.transform import scale


class DISPLAY:

    screen_size: tuple[int, int] = (640, 360)  # NO, YOU CAN'T MAKE A GAME THAT UGLY !!!!!1!
    screen: Surface = pg_display.set_mode(screen_size, FULLSCREEN | SCALED)  # 360p go brrrrrr
    CLOCK: Clock = Clock()
    FPS: int = 30
    delta_time: float = 0.  # Time since the last frame in seconds

    @classmethod
    def update(cls):
        pg_display.update()
        cls.delta_time = cls.CLOCK.tick(cls.FPS) / 1000

    @classmethod
    def display(cls, surface: Surface):
        cls.screen.blit(surface, (0, 0))

