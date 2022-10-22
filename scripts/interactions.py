from abc import ABC, abstractmethod

from pygame.mixer import find_channel, Channel, Sound

from scripts.text import TEXT
from scripts.utils import distance, join_path, set_stereo_volume
from scripts.visuals import VISUALS


class Interaction(ABC):
    @abstractmethod
    def __init__(self, *args, **kwargs):
        ...

    @abstractmethod
    def can_interact(self, player) -> bool:
        """Test if there is an interaction with the player."""
        ...

    @abstractmethod
    def interact(self, player):
        """Interact with the player."""
        ...

    @abstractmethod
    def update(self, player):
        """Update the interation each frame."""
        ...


class Test_Interaction(Interaction):
    def __init__(self, pos):
        self.pos = pos
        self.channel: Channel = find_channel(True)
        self.sound: Sound = Sound(join_path("data", "sounds", "sfx", "test.ogg"))

    def can_interact(self, player) -> bool:
        if player.is_looking_at(self.pos) and distance(player.pos, self.pos) < 3:
            TEXT.replace("see the test interaction", duration=0.0, fade_out=0.3)
            return True
        return False

    def interact(self, player):
        print("interact with the test interaction")
        VISUALS.shake = 1.0
        VISUALS.vignette = 1.0
        VISUALS.fish_eye = 1.0
        VISUALS.distortion = 1.0
        VISUALS.fried = 1.0

    def update(self, player):
        from scripts.game_logic import GAME_LOGIC

        GAME_LOGIC.RAY_CASTER.add_light(
            *self.pos, 1.,
            1., 0, 0,
        )

        set_stereo_volume(player, self.pos, self.channel)

        if self.channel.get_busy():
            return
        # self.channel.play(self.sound)
