from random import randint

from pygame.font import Font
from pygame import Surface
from pygame.mixer import stop as pg_mixer_stop, Sound

from scoreunlocked import Client as ScoreUnlockedClient

from scripts.display import DISPLAY
from scripts.text import TEXT
from scripts.input_handler import INPUT
from scripts.visuals import VISUALS
from scripts.utils import load_image, join_path

score_client = ScoreUnlockedClient()
score_client.connect('yvant2000', 'noctrum')

arcade_image: Surface = load_image("data", "main_menu", "arcade.png")


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
    arcade_image: Surface = arcade_image
    best_score_image: Surface = load_image("data", "main_menu", "best_score.png")

    bip_sound: Sound = Sound(join_path("data", "sounds", "sfx", "bip.ogg"))

    score: int = 0
    endless: bool = False

    best_score: bool = False
    char_selected: int = 0

    press_left: bool = False
    press_right: bool = False
    press_up: bool = False
    validate: bool = False

    leaderboard = []

    @classmethod
    def reset(cls, endless: bool = False, score: int = 0):
        from scripts.main_menu import MAIN_MENU
        cls.score = score
        cls.endless = endless
        cls.screamer_duration = 1.2
        pg_mixer_stop()
        cls.alpha = -1.
        cls.best_score = False
        cls.char_selected = 0
        cls.validate = False

        if cls.killer:
            cls.screamer_surface = load_image("data", "images", "visuals", f"{cls.killer}.png")
            cls.screamer_sound = Sound(join_path("data", "sounds", "screamers", f"{cls.killer}.ogg"))
            cls.screamer_sound.play()
            if not cls.endless:
                TEXT.replace(cls.reason, duration=60, fade_out=5, color=(50, 50, 50), size=8, y=350)
        else:
            Sound(join_path("data", "sounds", "sfx", "corridor_click.ogg")).play()
            if not MAIN_MENU.main_game_beaten:
                MAIN_MENU.main_game_beaten = True
                MAIN_MENU.reload_buttons()
                TEXT.replace("", duration=3.0, fade_out=0, size=32)
                TEXT.add("Endless mode unlocked.", duration=30, fade_out=5, color=(50, 150, 50), size=16)
                with open("save.txt", "w") as file:
                    file.write("True\n0\nKID")

        if endless:
            if score > MAIN_MENU.endless_mode_score:
                MAIN_MENU.endless_mode_score = score
                cls.best_score = True

            font = Font(join_path("data", "fonts", "PressStart2P.ttf"), 16)
            temp = font.render(f"Your score: {int(score)}", True, (100, 100, 150))
            cls.arcade_image.blit(temp, (cls.arcade_image.get_width() // 2 - temp.get_width() // 2, 312))

            cls.arcade_image = arcade_image.copy()
            y = 170
            for i, score in enumerate(cls.leaderboard):
                if i >= 5:
                    break
                temp: Surface = font.render(f"{i + 1}. {score[0]} - {score[1]}", True, (100, 100, 150))
                cls.arcade_image.blit(temp, (cls.arcade_image.get_width()//2 - temp.get_width()//2, y))
                y += temp.get_height() * 1.5

    @classmethod
    def get_leaderboard(cls):
        cls.leaderboard = score_client.get_leaderboard()

    @classmethod
    def update(cls) -> bool:

        if cls.endless:
            if cls.best_score:
                from scripts.main_menu import MAIN_MENU
                DISPLAY.screen.blit(cls.best_score_image, (0, 0))

                font = Font(join_path("data", "fonts", "PressStart2P.ttf"), 32)
                for i in range(3):
                    if i == cls.char_selected and not cls.validate:
                        font.set_underline(True)
                    else:
                        font.set_underline(False)
                    DISPLAY.screen.blit(font.render(MAIN_MENU.pseudo[i], True, (150, 150, 160)), (200 + 100 * i, 240))
                font = Font(join_path("data", "fonts", "PressStart2P.ttf"), 16)
                if cls.validate:
                    font.set_underline(True)
                temp = font.render("SUBMIT", True, (150, 150, 150))
                DISPLAY.screen.blit(temp, (DISPLAY.screen.get_width() // 2 - temp.get_width() // 2, 300))

                if cls.alpha >= 1:
                    if INPUT.left():
                        if not cls.press_left:
                            cls.bip_sound.play()
                            cls.char_selected = (cls.char_selected - 1) % 3
                            cls.press_left = True
                    else:
                        cls.press_left = False

                    if INPUT.right():
                        if not cls.press_right:
                            cls.bip_sound.play()
                            cls.char_selected = (cls.char_selected + 1) % 3
                            cls.press_right = True
                    else:
                        cls.press_right = False

                    if INPUT.up() or INPUT.down():
                        if not cls.press_up:
                            cls.bip_sound.play()
                            cls.validate = not cls.validate
                            cls.press_up = True
                    else:
                        cls.press_up = False

                    if INPUT.confirm():
                        if cls.validate:
                            cls.best_score = False
                            score_client.post_score(MAIN_MENU.pseudo, cls.score)
                            with open("save.txt", "w") as file:
                                file.write(f"True\n{int(cls.score)}\n{MAIN_MENU.pseudo}")
                        else:
                            MAIN_MENU.pseudo = MAIN_MENU.pseudo[:cls.char_selected] + chr((ord(MAIN_MENU.pseudo[cls.char_selected]) - 64) % 26 + 65) + MAIN_MENU.pseudo[cls.char_selected+1:]
            else:
                DISPLAY.screen.blit(cls.arcade_image, (0, 0))
                if cls.alpha >= 1:
                    if INPUT.confirm():
                        VISUALS.reset()
                        return True
        else:
            if cls.killer:
                DISPLAY.screen.blit(cls.screen, (0, 0))
            else:
                if not randint(0, int(4 / DISPLAY.delta_time)):
                    DISPLAY.screen.blit(cls.ew_win_image, (0, 0))
                else:
                    DISPLAY.screen.blit(cls.win_image, (0, 0))

            if cls.alpha >= 1:
                if INPUT.confirm():
                    VISUALS.reset()
                    return True

            TEXT.update()

        black = Surface(DISPLAY.screen_size)
        black.fill((0, 0, 0))
        black.set_alpha(max(0, int((1 - cls.alpha) * 255)))

        cls.alpha += DISPLAY.delta_time * 0.25
        DISPLAY.screen.blit(black, (0, 0))

        if cls.screamer_duration > 0 and cls.killer:
            cls.screamer_duration -= DISPLAY.delta_time
            DISPLAY.display_scaled(cls.screamer_surface)
            VISUALS.shake = 1.0
            VISUALS.fish_eye = 0.6
            VISUALS.display()

        return False
