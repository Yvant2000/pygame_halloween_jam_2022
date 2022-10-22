from abc import ABC, abstractmethod

from random import randint

from pygame.mixer import Sound, Channel, find_channel

from scripts.visuals import VISUALS
from scripts.display import DISPLAY
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
        self.z = 0
        self.width = 1
        self.height = 2.
        self.state = 0
        self.timer = 0.

        self.rope_sound = Sound(join_path("data", "sounds", "sfx", "rope.ogg"))
        self.channel: Channel | None = None
        self.danger_sound = Sound(join_path("data", "sounds", "sfx", "hangman_danger.ogg"))
        self.danger_channel: Channel | None = None

    def update(self):
        """Update the monster each frame."""
        from scripts.game_logic import GAME_LOGIC

        if not self.aggressiveness:
            return

        if self.state:
            set_stereo_volume(GAME_LOGIC.PLAYER, (self.x, 1, self.z), self.channel)
            self.danger_channel.set_volume(self.madness)
            if GAME_LOGIC.PLAYER.is_looking_at((self.x, 1.4, self.z), 1.3):
                self.madness += DISPLAY.delta_time * (1 + self.aggressiveness / 5) * 0.2
                VISUALS.fish_eye += 1.2 * DISPLAY.delta_time
                VISUALS.vignette += 1.7 * DISPLAY.delta_time
                VISUALS.distortion += 1.2 * DISPLAY.delta_time
                VISUALS.shake += 1.2 * DISPLAY.delta_time
                VISUALS.fried += 1.2 * DISPLAY.delta_time
            else:
                self.madness -= DISPLAY.delta_time * 0.2

            print(self.madness)

            # TODO: Add Game Over screen

        if GAME_LOGIC.time_stopped:
            return

        self.timer -= DISPLAY.delta_time * randint(1, 3) / 3
        if self.timer <= 0:
            self.state = not self.state
            if self.state:
                self.timer = 10 + self.aggressiveness
                self.channel = find_channel(True)
                self.channel.play(self.rope_sound, loops=-1)
                self.danger_channel = find_channel(True)
                self.danger_channel.play(self.danger_sound, loops=-1)
                self.x = randint(-1, 2)
                self.z = randint(-2, 3)
            else:
                self.channel.stop()
                self.danger_channel.stop()
                self.timer = 35 - self.aggressiveness

    def draw(self):
        """Draw the monster each frame."""
        if self.state > 0:
            from scripts.game_logic import GAME_LOGIC
            add_surface_toward_player_2d(
                GAME_LOGIC.RAY_CASTER,
                GAME_LOGIC.PLAYER,
                self.image,
                (self.x, 1, self.z),
                self.width,
                self.height,
            )

