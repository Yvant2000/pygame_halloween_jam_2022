from pygame import Surface
from pygame.mixer import stop as pg_mixer_stop, Sound

from scripts.display import DISPLAY
from scripts.text import TEXT
from scripts.input_handler import INPUT
from scripts.utils import load_image, join_path


class GAME_OVER_SCREEN:

    reason: str = ''
    killer: str = ''
    alpha: float = 0

    screamer_duration: float = 0
    screamer_surface: Surface = None
    screamer_sound: Sound = None

    screen: Surface = load_image("data", "main_menu", "game_over.png")

    @classmethod
    def reset(cls):
        cls.screamer_duration = 1.2
        pg_mixer_stop()
        cls.alpha = -1.
        TEXT.replace(cls.reason, duration=25, fade_out=5, color=(50, 50, 50), size=8)

        cls.screamer_surface = load_image("data", "images", "visuals", f"{cls.killer}.png")
        cls.screamer_sound = Sound(join_path("data", "sounds", "screamers", f"{cls.killer}.ogg"))
        cls.screamer_sound.play()

    @classmethod
    def update(cls) -> bool:

        black = Surface(DISPLAY.screen_size)
        black.fill((0, 0, 0))
        black.set_alpha(max(0, int((1 - cls.alpha) * 255)))

        cls.alpha += DISPLAY.delta_time * 0.25

        DISPLAY.screen.blit(cls.screen, (0, 0))
        TEXT.update()
        DISPLAY.screen.blit(black, (0, 0))

        if cls.screamer_duration > 0:
            cls.screamer_duration -= DISPLAY.delta_time
            DISPLAY.display_scaled(cls.screamer_surface)

        if cls.alpha >= 1:
            if INPUT.confirm():
                return True

        return False
