from abc import ABC, abstractmethod

from pygame import Surface
from pygame.mixer import find_channel, Channel, Sound

from scripts.text import TEXT
from scripts.utils import distance, join_path, set_stereo_volume, load_image, add_surface_toward_player_2d
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


class BedsideLamp(Interaction):
    def __init__(self, pos):
        self.pos: tuple[float, float, float] = pos
        self.light: bool = False
        self.click_sound: Sound = Sound(join_path("data", "sounds", "sfx", "click.ogg"))
        self.image: Surface = load_image("data", "images", "props", "bedsidelight.png")

    def can_interact(self, player) -> bool:
        if player.is_looking_at(self.pos) and distance(player.pos, self.pos) < 2:
            TEXT.replace("Turn off the light" if self.light else "Turn on the light", duration=0.0, fade_out=0.3, color=(100, 100, 100))
            return True
        return False

    def interact(self, player):
        self.light = not self.light
        player.bedside_light = self.light
        self.click_sound.play()

    def update(self, player):
        from scripts.game_logic import GAME_LOGIC

        if self.light:
            # {"x", "y", "z", "intensity", "red", "green", "blue", "direction_x", "direction_y", "direction_z", NULL};
            GAME_LOGIC.RAY_CASTER.add_light(
                *self.pos, 3.,
                0.9, 0.8, 0.4,
                self.pos[0] + 0.01, self.pos[1] + 2.5, self.pos[2] + 0.01,
            )

            GAME_LOGIC.RAY_CASTER.add_light(
                *self.pos, 1.,
                0.9, 0.8, 0.4,
            )

        add_surface_toward_player_2d(
            GAME_LOGIC.RAY_CASTER,
            player,
            self.image,
            self.pos,
            0.5,
            0.5,
        )


class Bed(Interaction):
    def __init__(self, pos):
        self.pos = pos

    def can_interact(self, player) -> bool:
        if player.is_looking_at(self.pos) and distance(player.pos, self.pos) < 3:
            TEXT.replace("Go to bed", duration=0.0, fade_out=0.3, color=(100, 100, 100))
            return True
        return False

    def interact(self, player):
        player.in_bed = True

    def update(self, player):
        if player.in_bed:
            TEXT.replace("JUMP to leave the bed", duration=0., fade_out=0.3, color=(100, 100, 100))


class FlashLight(Interaction):
    def __init__(self, pos):
        self.pos = pos
        self.image: Surface = load_image("data", "images", "props", "flashlight.png")

    def can_interact(self, player) -> bool:
        if player.is_looking_at(self.pos) and distance(player.pos, self.pos) < 2.0:
            TEXT.replace("Get the flashlight", duration=0.0, fade_out=0.3, color=(100, 100, 100))
            return True
        return False

    def interact(self, player):
        from scripts.game_logic import GAME_LOGIC
        player.have_flashlight = True
        player.use_flashlight = True
        TEXT.replace("RIGHT CLICK to turn off the light")
        GAME_LOGIC.interaction_list.remove(self)

    def update(self, player):
        from scripts.game_logic import GAME_LOGIC
        add_surface_toward_player_2d(
            GAME_LOGIC.RAY_CASTER,
            player,
            self.image,
            self.pos,
            0.5,
            0.5,
        )
