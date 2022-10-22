from typing import Generator
from math import sin, pi

from pygame.transform import scale
from pygame import Surface


from scripts.display import DISPLAY
from scripts.input_handler import INPUT
from scripts.utils import lazy_load_images


class SplashScreen:
    SPLASH_DURATION: float = 2.5

    def __init__(self):
        self.splash_generator: Generator = lazy_load_images("data", "splash_screen")
        self.surface: Surface = Surface(DISPLAY.screen_size)
        self._splash_image: Surface | None = None
        self._counter: float = 0.

    def next(self) -> bool:
        """Set the splash image to the next image in the generator and return True if there is no more image.
        @return: True if there is no more image, False otherwise.
        """
        try:
            self._splash_image = next(self.splash_generator)
        except StopIteration:
            return True
        else:  # ngl, the else is useless here, but I like it because it's an obscure feature
            return False

    def blit(self) -> None:
        """Blit the splash image on the screen."""

        alpha: int = int(sin(pi * (self._counter / SplashScreen.SPLASH_DURATION)) * 255)

        self.surface.fill((0, 0, 0))  # Clear the screen

        facto: float = 1 - (self._counter / SplashScreen.SPLASH_DURATION) * 0.1
        temp = scale(self._splash_image, (self.surface.get_width() * facto, self.surface.get_height() * facto))

        temp.set_alpha(alpha)
        temp_center: tuple[int, int] = temp.get_rect().center
        surface_center: tuple[int, int] = self.surface.get_rect().center
        self.surface.blit(temp, (surface_center[0] - temp_center[0], surface_center[1] - temp_center[1]))

    def update(self) -> bool:
        """Update the splash screen.

        @return: True if all the images have been displayed, False otherwise.
        """
        if self._counter <= 0. or INPUT.confirm():
            if self.next():
                return True
            self._counter = SplashScreen.SPLASH_DURATION

        self.blit()
        DISPLAY.display(self.surface)
        self._counter -= DISPLAY.delta_time
        return False


SPLASH_SCREEN: SplashScreen = SplashScreen()
