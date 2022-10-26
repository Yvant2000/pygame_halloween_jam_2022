from random import randint

from pygame import Surface
from pygame.mixer import stop as pg_mixer_stop, Sound

from scripts.display import DISPLAY
from scripts.text import TEXT
from scripts.input_handler import INPUT
from scripts.visuals import VISUALS
from scripts.utils import load_image, join_path


class GAME_OVER_SCREEN:

    reason: str = ''
    killer: str = ''
    alpha: float = 0

    screamer_duration: float = 0
    screamer_surface: Surface = None
    screamer_sound: Sound = None

    screen: Surface = load_image("data", "main_menu", "game_over.png")
    win_image: Surface = load_image("data", "main_menu", "win.png")
    ew_win_image: Surface = load_image("data", "main_menu", "win_.png")

    score: int = 0
    endless: bool = False

    @classmethod
    def reset(cls, endless: bool = False, score: int = 0):
        cls.screamer_duration = 1.2
        pg_mixer_stop()
        cls.alpha = -1.

        if cls.killer:
            cls.screamer_surface = load_image("data", "images", "visuals", f"{cls.killer}.png")
            cls.screamer_sound = Sound(join_path("data", "sounds", "screamers", f"{cls.killer}.ogg"))
            cls.screamer_sound.play()
            TEXT.replace(cls.reason, duration=25, fade_out=5, color=(50, 50, 50), size=8, y=340)
        else:
            Sound(join_path("data", "sounds", "sfx", "corridor_click.ogg")).play()
            from scripts.main_menu import MAIN_MENU
            if not MAIN_MENU.main_game_beaten:
                MAIN_MENU.main_game_beaten = True
                TEXT.replace("", duration=2.0, fade_out=0, color=(50, 100, 50), size=32)
                TEXT.add("Endless mode unlocked.", duration=25, fade_out=5, color=(50, 100, 50), size=32)
                with open("save.txt", "w") as file:
                    file.write("True\n0")

        cls.score = score
        cls.endless = endless

    @classmethod
    def update(cls) -> bool:

        black = Surface(DISPLAY.screen_size)
        black.fill((0, 0, 0))
        black.set_alpha(max(0, int((1 - cls.alpha) * 255)))

        cls.alpha += DISPLAY.delta_time * 0.25

        if cls.endless:
            ...  # TODO: game over screen for endless mode
        else:
            if cls.killer:
                DISPLAY.screen.blit(cls.screen, (0, 0))
            else:
                if not randint(1, int(5 / DISPLAY.delta_time)):
                    DISPLAY.screen.blit(cls.ew_win_image, (0, 0))
                else:
                    DISPLAY.screen.blit(cls.win_image, (0, 0))

        TEXT.update()

        DISPLAY.screen.blit(black, (0, 0))

        if cls.screamer_duration > 0 and cls.killer:
            cls.screamer_duration -= DISPLAY.delta_time
            DISPLAY.display_scaled(cls.screamer_surface)
            VISUALS.shake = 1.0
            VISUALS.display()

        if cls.alpha >= 1:
            if INPUT.confirm():
                return True

        return False
