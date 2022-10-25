from abc import ABC, abstractmethod

from random import choice as random_choice
from math import sin, radians, cos

from pygame import Surface
from pygame.mixer import Channel, Sound

from scripts.game_logic import GAME_LOGIC
from scripts.text import TEXT
from scripts.utils import distance, join_path, set_stereo_volume, load_image, add_surface_toward_player_2d
from scripts.visuals import VISUALS
from scripts.display import DISPLAY


pickup_sound: Sound = Sound(join_path("data", "sounds", "sfx", "pickup.ogg"))


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
        self.channel: Channel = Channel(0)
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
        self.image_off: Surface = load_image("data", "images", "props", "bedsidelight_off.png")
        self.image_on: Surface = load_image("data", "images", "props", "bedsidelight_on.png")

    def can_interact(self, player) -> bool:
        if player.is_looking_at(self.pos, 0.4) and distance(player.pos, self.pos) < 2:
            TEXT.replace("Turn off the light" if self.light else "Turn on the light", duration=0.0, fade_out=0.3, color=(100, 100, 100))
            return True
        return False

    def interact(self, player):
        self.light = not self.light
        player.bedside_light = self.light
        self.click_sound.play()

    def update(self, player):
        if self.light:
            # {"z", "y", "z", "intensity", "red", "green", "blue", "direction_x", "direction_y", "direction_z", NULL};
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
            self.image_on if self.light else self.image_off,
            self.pos,
            0.5,
            0.5,
        )


class PissDrawer(Interaction):
    def __init__(self, pos):
        self.pos = pos

    def can_interact(self, player) -> bool:
        if player.is_looking_at(self.pos, 0.4) and distance(player.pos, self.pos) < 1.45:
            TEXT.replace("Open piss drawer", duration=0.0, fade_out=0.3, color=(150, 150, 20))
            return True
        return False

    def interact(self, player):
        GAME_LOGIC.interaction_list.remove(self)
        VISUALS.fried = 1.5

    def update(self, player):
        ...


class Bed(Interaction):
    def __init__(self, pos):
        self.pos = pos
        self.sound: Sound = Sound(join_path("data", "sounds", "sfx", "bed2.ogg"))

    def can_interact(self, player) -> bool:
        if player.is_looking_at(self.pos) and distance(player.pos, self.pos) < 3:
            TEXT.replace("Go to bed", duration=0.0, fade_out=0.3, color=(100, 100, 100))
            return True
        return False

    def interact(self, player):
        player.in_bed = True
        self.sound.play()

    def update(self, player):
        if player.in_bed:
            TEXT.replace("JUMP to leave the bed", duration=0., fade_out=0.3, color=(100, 100, 100))


class FlashLight(Interaction):
    def __init__(self, pos):
        self.pos = pos
        self.image: Surface = load_image("data", "images", "props", "flashlight.png")

    def can_interact(self, player) -> bool:
        if player.is_looking_at(self.pos, 0.5) and distance(player.pos, self.pos) < 2.0:
            TEXT.replace("Get the flashlight", duration=0.0, fade_out=0.3, color=(100, 100, 100))
            return True
        return False

    def interact(self, player):
        player.has_flashlight = True
        player.use_flashlight = True
        pickup_sound.play()
        TEXT.replace("RIGHT CLICK to turn off the light", force=True)
        GAME_LOGIC.interaction_list.remove(self)

    def update(self, player):
        add_surface_toward_player_2d(
            GAME_LOGIC.RAY_CASTER,
            player,
            self.image,
            self.pos,
            0.5,
            0.5,
        )


class Wardrobe(Interaction):
    def __init__(self, door_pos, enter_pos):
        self.enter_pos = enter_pos
        self.door_pos = door_pos

        self.x: float = 0.

        self.door_image: Surface = load_image("data", "images", "props", "wardrobe_left_door.png")
        self.sound: Sound = Sound(join_path("data", "sounds", "sfx", "wardrobe.ogg"))

    def can_interact(self, player) -> bool:
        if player.is_looking_at((self.door_pos[0] - self.x - 0.4, *(self.door_pos[1:])), 0.5) and distance(player.pos, self.door_pos) < 2.0:
            TEXT.replace("Close the wardrobe" if GAME_LOGIC.wardrobe_open else "Open the wardrobe", duration=0.0, fade_out=0.3, color=(100, 100, 100))
            return True

        if GAME_LOGIC.wardrobe_open and player.is_looking_at(self.enter_pos, 0.8) and distance(player.pos, self.door_pos) < 1.2:
            TEXT.replace("Enter the wardrobe", duration=0.0, fade_out=0.3, color=(100, 100, 100))
            return True
        return False

    def interact(self, player):
        if player.is_looking_at((self.door_pos[0] - self.x - 0.4, *(self.door_pos[1:])), 0.5) and distance(player.pos, self.door_pos) < 2.0:
            GAME_LOGIC.wardrobe_open = not GAME_LOGIC.wardrobe_open
            self.sound.stop()
            self.sound.play()
        else:
            player.in_wardrobe = True

    def update(self, player):
        if GAME_LOGIC.wardrobe_open:
            self.x = min(0.70, self.x + 1.2 * DISPLAY.delta_time)
        else:
            self.x = max(0., self.x - 1.2 * DISPLAY.delta_time)

        GAME_LOGIC.RAY_CASTER.add_surface(
            self.door_image,
            self.door_pos[0] - self.x, 2.0, self.door_pos[2],
            self.door_pos[0] - self.x - 0.8, 0.0, self.door_pos[2],
            rm=True)


class BabyPhone(Interaction):
    def __init__(self, pos):
        self.pos = pos
        self.image: Surface = load_image("data", "images", "props", "babyphone.png")
        self.image_alert: Surface = load_image("data", "images", "props", "babyphone_alert.png")
        self.image_on: Surface = load_image("data", "images", "props", "babyphone_on.png")

        self.alert: bool = False
        self.channel: Channel = Channel(1)
        self.default_sound: Sound = Sound(join_path("data", "sounds", "sfx", "white_noise.ogg"))

    def can_interact(self, player) -> bool:
        if self.channel.get_busy():
            return False

        if player.is_looking_at(self.pos, 0.4) and distance(player.pos, self.pos) < 2.0:
            TEXT.replace("Listen to the baby-phone", duration=0.0, fade_out=0.3, color=(100, 100, 100))
            return True
        return False

    def interact(self, player):
        if not self.alert:
            self.channel.play(self.default_sound, loops=1)

        # TODO

    def update(self, player):
        if self.channel.get_busy():
            set_stereo_volume(GAME_LOGIC.PLAYER, self.pos, self.channel)
            return add_surface_toward_player_2d(
                GAME_LOGIC.RAY_CASTER,
                player,
                self.image_on,
                self.pos,
                0.5,
                0.5,
            )

        if self.alert:
            # {"z", "y", "z", "intensity", "red", "green", "blue", "direction_x", "direction_y", "direction_z", NULL};
            GAME_LOGIC.RAY_CASTER.add_light(
                *self.pos,
                0.8,
                0.8, 0.2, 0.3,
            )
            return add_surface_toward_player_2d(
                GAME_LOGIC.RAY_CASTER,
                player,
                self.image_alert,
                self.pos,
                0.5,
                0.5,
            )
        add_surface_toward_player_2d(
            GAME_LOGIC.RAY_CASTER,
            player,
            self.image,
            self.pos,
            0.5,
            0.5,
        )


class TeddyBear(Interaction):
    def __init__(self):
        self.pos: tuple[float, float, float] = random_choice((
            (-2.26, 0.0, 2.2),
            (-2.0, 1.1, 2.4),
            (2.0, 0.0, 3.3),
            (1.3, -0.1, -3.18),
            (-2.0, 0.0, -3.3),
            (2.3, 0.0, -3.3),
            (0, 0, 0),
        ))
        self.image: Surface = load_image("data", "images", "props", "teddy_bear.png")

    def can_interact(self, player) -> bool:
        if player.is_looking_at(self.pos, 0.7) and distance(player.pos, self.pos) < 1.8:
            TEXT.replace("Pick up George", duration=0.0, fade_out=0.3, color=(100, 100, 100))
            return True
        return False

    def interact(self, player):
        GAME_LOGIC.interaction_list.remove(self)
        pickup_sound.play()
        player.has_teddy_bear = True

    def update(self, player):
        add_surface_toward_player_2d(
            GAME_LOGIC.RAY_CASTER,
            player,
            self.image,
            self.pos,
            0.5,
            0.5,
        )
        if not GAME_LOGIC.PLAYER.use_flashlight and not GAME_LOGIC.PLAYER.bedside_light:
            # {"z", "y", "z", "intensity", "red", "green", "blue", "direction_x", "direction_y", "direction_z", NULL};
            GAME_LOGIC.RAY_CASTER.add_light(
                self.pos[0], self.pos[1] + 0.2, self.pos[2],
                0.4,
                0.8, 0.8, 0.1,
            )


class MimicGift(Interaction):
    def __init__(self, pos):
        self.pos = pos

    def can_interact(self, player) -> bool:
        if player.has_teddy_bear and player.is_looking_at(self.pos, 0.7) and distance(player.pos, self.pos) < 2.5:
            TEXT.replace("Give back the friend", duration=0.0, fade_out=0.3, color=(100, 100, 100))
            return True
        return False

    def interact(self, player):
        player.has_teddy_bear = False
        GAME_LOGIC.monster_list['Mimic'].calm()  # type: ignore

    def update(self, player):
        ...


class Door(Interaction):
    def __init__(self, pos):
        self.image: Surface = load_image("data", "images", "props", "door.png")
        self.pos = pos
        self.angle: float = 0

    def can_interact(self, player) -> bool:
        if player.is_looking_at((self.pos[0] - sin(radians(self.angle)) * 0.4, self.pos[1], self.pos[2] - cos(radians(self.angle)) * 0.4), 0.4) and distance(player.pos, self.pos) < 2.0:
            TEXT.replace("Close the door" if GAME_LOGIC.door_open else "Open the door", duration=0.0, fade_out=0.3, color=(100, 100, 100))
            return True
        return False

    def interact(self, player):
        GAME_LOGIC.door_open = not GAME_LOGIC.door_open

    def update(self, player):

        if GAME_LOGIC.door_open:
            self.angle = min(90., self.angle + DISPLAY.delta_time * 110)
        else:
            self.angle = max(0., self.angle - DISPLAY.delta_time * 110)

        GAME_LOGIC.RAY_CASTER.add_surface(
            self.image,
            self.pos[0], 2.0, self.pos[2],
            self.pos[0] - sin(radians(self.angle)) * 0.8, 0.0, self.pos[2] - cos(radians(self.angle)) * 0.8,
            rm=True
        )


class Window(Interaction):
    def __init__(self, pos):
        self.image = load_image("data", "images", "props", "window.png")
        self.pos = pos
        self.y = 0.0

    def can_interact(self, player) -> bool:
        if not self.y:
            return False

        if player.is_looking_at((self.pos[0], self.pos[1] + self.y, self.pos[2] - 0.4), 0.4) and distance(player.pos, self.pos) < 1.5:
            TEXT.replace("Close the window", duration=0.0, fade_out=0.3, color=(100, 100, 100))
            return True
        return False

    def interact(self, player):
        # TODO: add sound
        self.y = 0

    def update(self, player):
        # TODO: play_outside_sound
        GAME_LOGIC.RAY_CASTER.add_surface(
            self.image,
            self.pos[0], self.pos[1] + 0.5 + self.y, self.pos[2] - 0.8,
            self.pos[0], self.pos[1] + self.y, self.pos[2],
            rm=True
        )
