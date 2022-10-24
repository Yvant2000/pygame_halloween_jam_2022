from abc import ABC, abstractmethod

from random import randint
from math import sin

from pygame.mixer import Sound, Channel

from scripts.visuals import VISUALS
from scripts.display import DISPLAY
from scripts.text import TEXT
from scripts.game_over import GAME_OVER_SCREEN
from scripts.utils import load_image, add_surface_toward_player_2d, join_path, set_stereo_volume


class Monster(ABC):
    @abstractmethod
    def __init__(self, *args, **kwargs):
        self.state: int = 0
        self.aggressiveness: int = 0
        self.timer: float = 0.0

    @abstractmethod
    def update(self):
        """Update the monster each frame."""
        ...

    @abstractmethod
    def draw(self):
        """Draw the monster each frame."""
        ...


class Hangman(Monster):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.madness: int = 0

        self.image = load_image("data", "images", "monsters", "hangman.png")
        self.x = 0
        self.y = 2.0
        self.z = 0
        self.width = 1
        self.height = 2.5
        self.state = 0
        self.timer = 30.

        self.rope_sound = Sound(join_path("data", "sounds", "sfx", "rope.ogg"))
        self.channel: Channel = Channel(2)
        self.danger_sound = Sound(join_path("data", "sounds", "sfx", "hangman_danger.ogg"))
        self.danger_channel: Channel = Channel(3)

    def update(self):
        """Update the monster each frame."""
        from scripts.game_logic import GAME_LOGIC

        if not self.aggressiveness:
            return

        if self.state:
            self.y = max(0., self.y - DISPLAY.delta_time)
            set_stereo_volume(GAME_LOGIC.PLAYER, (self.x, 1, self.z), self.channel)
            if GAME_LOGIC.PLAYER.is_looking_at((self.x, 1.4 + self.y, self.z), 1.5):
                if len(TEXT.text_list) < 2:
                    TEXT.add(
                        " " * randint(0, 5) + "LOOK AT ME" + " " * randint(0, 5),
                        duration=0.08, fade_out=0., color=(50, 5, 5), font="HelpMe",
                        y=randint(50, DISPLAY.screen_size[1] - 50), size=int(32 * (1 + self.madness))
                    )

                self.madness += DISPLAY.delta_time * (1 + self.aggressiveness / 5) * 0.2
                VISUALS.fish_eye += 2.0 * DISPLAY.delta_time
                VISUALS.vignette += 1.7 * DISPLAY.delta_time
                VISUALS.distortion += 1.2 * DISPLAY.delta_time
                VISUALS.shake += 1.2 * DISPLAY.delta_time
                # VISUALS.fried += 1.2 * DISPLAY.delta_time
            else:
                self.madness -= DISPLAY.delta_time * 0.2

            self.danger_channel.set_volume(self.madness)

            if self.madness > 1.0:
                GAME_OVER_SCREEN.reason = "Don't look at the hangman. Listen carefully for the rope."
                GAME_LOGIC.game_over()

        if GAME_LOGIC.time_stopped:
            return

        self.timer -= DISPLAY.delta_time * randint(1, 3) / 3
        if self.timer <= 0:
            self.state = not self.state
            if self.state:
                self.timer = 10 + self.aggressiveness
                self.channel.play(self.rope_sound, loops=-1)
                self.danger_channel.set_volume(0, 0)
                self.danger_channel.play(self.danger_sound, loops=-1)
                self.x = randint(-1, 2)
                self.z = randint(-2, 3)
            else:
                self.channel.stop()
                self.danger_channel.stop()
                self.danger_channel.set_volume(0)
                self.timer = 35 - self.aggressiveness
                self.madness = 0.
                self.y = 2.0

    def draw(self):
        """Draw the monster each frame."""
        if self.state > 0:
            from scripts.game_logic import GAME_LOGIC
            add_surface_toward_player_2d(
                GAME_LOGIC.RAY_CASTER,
                GAME_LOGIC.PLAYER,
                self.image,
                (self.x + sin(self.timer) / 10, 0.5 + self.y, self.z),
                self.width,
                self.height,
            )


class Mimic(Monster):
    def __init__(self):
        super().__init__()

        self.front_image = load_image("data", "images", "props", "chest_front.png")
        self.side_image = load_image("data", "images", "props", "chest_side.png")
        self.top_image = load_image("data", "images", "props", "chest_top.png")

    def update(self):
        """Update the monster each frame."""
        ...

    def draw(self):
        """Draw the monster each frame."""

        if self.state == 0:
            self.draw_chest()
            return

    def draw_chest(self):
        from scripts.game_logic import GAME_LOGIC

        # {"image", "A_x", "A_y", "A_z", "B_x", "B_y", "B_z","C_x", "C_y", "C_z", "rm", NULL};
        GAME_LOGIC.RAY_CASTER.add_surface(
            self.front_image,
            -1.9, 0.41, -0.95,
            -1.9, 0.0, 0.35,
            rm=True,
        )
        GAME_LOGIC.RAY_CASTER.add_surface(
            self.side_image,
            -2.5, 0.6, -0.95,
            -1.9, 0.0, -0.95,
            rm=True,
        )
        GAME_LOGIC.RAY_CASTER.add_surface(
            self.side_image,
            -2.5, 0.6, 0.35,
            -1.9, 0.0, 0.35,
            rm=True,
        )
        GAME_LOGIC.RAY_CASTER.add_surface(
            self.top_image,
            -2.31, 0.6, -0.95,
            -2.09, 0.6, 0.35,
            -2.09, 0.6, -0.95,
            rm=True,
        )

        GAME_LOGIC.RAY_CASTER.add_surface(
            self.top_image,
            -2.1, 0.6, -0.95,
            -1.89, 0.4, 0.35,
            -1.89, 0.4, -0.95,
            rm=True,
        )

        GAME_LOGIC.RAY_CASTER.add_surface(
            self.top_image,
            -2.3, 0.6, -0.95,
            -2.5, 0.4, 0.35,
            -2.5, 0.4, -0.95,
            rm=True,
        )
