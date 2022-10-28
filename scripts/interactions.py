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
        self.click_sound: Sound = Sound(join_path("data", "sounds", "sfx", "bedlight.ogg"))
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
        self.sound: Sound = Sound(join_path("data", "sounds", "sfx", "white_noise_hit.ogg"))

    def can_interact(self, player) -> bool:
        if player.is_looking_at(self.pos, 0.4) and distance(player.pos, self.pos) < 1.4:
            TEXT.replace("Open the piss drawer", duration=0.0, fade_out=0.3, color=(150, 150, 20))
            return True
        return False

    def interact(self, player):
        self.sound.play()
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

        self.bip_sound: Sound = Sound(join_path("data", "sounds", "sfx", "bip.ogg"))

        self.channel: Channel = Channel(1)
        self.default_sound: Sound = Sound(join_path("data", "sounds", "sfx", "white_noise.ogg"))
        self.stopped_time: bool = False
        self.timer: float = 0.

    def can_interact(self, player) -> bool:
        if self.channel.get_busy():
            return False

        if player.is_looking_at(self.pos, 0.4) and distance(player.pos, self.pos) < 2.0:
            if GAME_LOGIC.time_stopped:
                TEXT.replace("Watch out.", duration=0.0, fade_out=0.3, color=(100, 80, 80))
                return False
            TEXT.replace("Listen to the baby-phone", duration=0.0, fade_out=0.3, color=(100, 100, 100))
            return True
        return False

    def interact(self, player):
        if not GAME_LOGIC.phone_alert:
            return self.channel.play(self.default_sound, loops=1)

        GAME_LOGIC.phone_alert = False
        self.stopped_time = True
        GAME_LOGIC.time_stopped = True
        match GAME_LOGIC.hour:
            case 0:
                self.channel.play(Sound(join_path("data", "sounds", "phone_rec", f"0.ogg")))
                TEXT.text_list = []
                TEXT.replace("", duration=1.5, fade_out=0., color=(50, 50, 100), force=True)  # 1.5
                TEXT.add("Hello ?", duration=1.5, fade_out=0., color=(50, 50, 100), force=True)  # 3.0
                TEXT.add("Can you hear me ?", duration=1., fade_out=0., color=(50, 50, 100), force=True)  # 4.0
                TEXT.add("Good evening my boy.", duration=1.75, fade_out=0., color=(50, 50, 100), force=True)  # 5.75
                TEXT.add("You have a little difficulty\nto fall asleep ?", duration=2.75, fade_out=0., color=(50, 50, 100), force=True)  # 8.5
                TEXT.add("Oh !", duration=0.5, fade_out=0., color=(50, 50, 100), force=True)  # 9.0
                TEXT.add("It's nothing !", duration=1.5, fade_out=0., color=(50, 50, 100), force=True)  # 10.5
                TEXT.add("I understand.", duration=1.20, fade_out=0., color=(50, 50, 100), force=True)  # 11.75
                TEXT.add("You know, me too at night sometimes\nI can't fall asleep.", duration=3.5, fade_out=0., color=(50, 50, 100), force=True)  # 15.25
                TEXT.add("But you know what I do\nwhen I can't sleep ?", duration=3.1, fade_out=0., color=(50, 50, 100), force=True)  # 18.5
                TEXT.add("I play with my friends !", duration=1.5, fade_out=0., color=(50, 50, 100), force=True)  # 20.
                TEXT.add("Do you want to play with us ?", duration=1.5, fade_out=0., color=(50, 50, 100), force=True)  # 21.5
                TEXT.add("You'll see,\nwe'll have a lot of fun !", duration=2.5, fade_out=0., color=(50, 50, 100), force=True)  # 24.0
                TEXT.add("How about we start\nwith a little lullaby...", duration=2.8, fade_out=0., color=(50, 50, 100), force=True)  # 27.0
                TEXT.add("...To explain the rules to you.", duration=3.0, fade_out=2.5, color=(100, 50, 50), force=True)
            case 1:
                self.channel.play(Sound(join_path("data", "sounds", "phone_rec", f"1.ogg")))
                TEXT.replace("", duration=4.5, fade_out=0., color=(50, 50, 100), force=True)
                TEXT.add("TIC TAC", duration=1.5, fade_out=0., color=(50, 50, 100), force=True)
                TEXT.add("One hour passed.", duration=2.0, fade_out=2.0, color=(50, 50, 100), force=True)
                TEXT.add("Look ! He's here ! The Eye in the night.", duration=4.0, fade_out=0., color=(50, 50, 100), force=True)
                TEXT.add("Looking for a warm light...", duration=2.0, fade_out=0., color=(50, 50, 100), force=True)
                TEXT.add("Give it to him what he wants.", duration=2.0, fade_out=0., color=(50, 50, 100), force=True)
                TEXT.add("Give him all you can.", duration=2.0, fade_out=2.5, color=(100, 50, 50), force=True)
            case 2:
                self.channel.play(Sound(join_path("data", "sounds", "phone_rec", f"2.ogg")))
                TEXT.replace("", duration=4.5, fade_out=0., color=(50, 50, 100), force=True)
                TEXT.add("TIC TAC", duration=1.5, fade_out=0., color=(50, 50, 100), force=True)
                TEXT.add("Two hours passed.", duration=2.0, fade_out=2.0, color=(50, 50, 100), force=True)
                TEXT.add("He comes from the dark;", duration=1.5, fade_out=0., color=(50, 50, 100), force=True)
                TEXT.add("The Guest we are waiting for.", duration=2.0, fade_out=0., color=(50, 50, 100), force=True)
                TEXT.add("He can't waits for diner...", duration=2.0, fade_out=0., color=(50, 50, 100), force=True)
                TEXT.add("But he have to wait outdoor...", duration=2.0, fade_out=2.5, color=(100, 50, 50), force=True)
            case 3:
                self.channel.play(Sound(join_path("data", "sounds", "phone_rec", f"3.ogg")))
                TEXT.replace("", duration=4.0, fade_out=0., color=(50, 50, 100), force=True)
                TEXT.add("TIC TAC", duration=1.5, fade_out=0., color=(50, 50, 100), force=True)
                TEXT.add("Three hours passed.", duration=2.0, fade_out=0.5, color=(50, 50, 100), force=True)
                TEXT.add("Be careful !", duration=2.0, fade_out=0., color=(50, 50, 100), force=True)  # 10
                TEXT.add("He's watching you", duration=1.5, fade_out=0., color=(50, 50, 100), force=True)  # 11.5
                TEXT.add("Inside his house made of wood.", duration=2.5, fade_out=0., color=(50, 50, 100), force=True)  # 14
                TEXT.add("The watcher is here and waits for you;", duration=2.5, fade_out=0.0, color=(50, 50, 100), force=True)  # 16.5
                TEXT.add("Light is only a friend of you.", duration=2.5, fade_out=2.5, color=(100, 50, 50), force=True)  # 16.5
            case 4:
                self.channel.play(Sound(join_path("data", "sounds", "phone_rec", f"4.ogg")))
                TEXT.replace("", duration=4.0, fade_out=0., color=(50, 50, 100), force=True)
                TEXT.add("TIC TAC", duration=1.5, fade_out=0., color=(50, 50, 100), force=True)
                TEXT.add("Four hours passed.", duration=2.0, fade_out=4.5, color=(50, 50, 100), force=True)  # 12
                TEXT.add("George is missing, Steven is crying.", duration=3.5, fade_out=0., color=(50, 50, 100), force=True)  # 15.5
                TEXT.add("Find George before his friend find you.", duration=2.5, fade_out=2.5, color=(100, 50, 50), force=True)
            case 5:
                self.channel.play(Sound(join_path("data", "sounds", "phone_rec", f"5.ogg")))
                TEXT.replace("", duration=3.5, fade_out=0., color=(50, 50, 100), force=True)  # 3.5
                TEXT.add("TIC TAC", duration=2.5, fade_out=0., color=(50, 50, 100), force=True)  # 6.0
                TEXT.add("Five hours passed.", duration=2.0, fade_out=3.0, color=(50, 50, 100), force=True)  # 11
                TEXT.add("Remember the monster under the bed ?", duration=2.5, fade_out=0., color=(50, 50, 100), force=True)  # 13.5
                TEXT.add("The crawling thing is not a legend yet.", duration=3.5, fade_out=0.0, color=(50, 50, 100), force=True)  # 17
                TEXT.add("He wants to play hide and seek, but...", duration=2.0, fade_out=0.0, color=(100, 50, 50), force=True)  # 20
                TEXT.add("He don't have friends.", duration=2.5, fade_out=2.5, color=(50, 50, 100), force=True)

            case 6:
                self.channel.play(Sound(join_path("data", "sounds", "phone_rec", f"6.ogg")))
                TEXT.replace("", duration=2.0, fade_out=0., color=(50, 50, 100), force=True)
                TEXT.add("TIC TAC", duration=4.0, fade_out=0., color=(50, 50, 100), force=True)
                TEXT.add("Six hours passed.", duration=2.0, fade_out=3.0, color=(50, 50, 100), force=True)  # 11
                TEXT.add("The sinner had made a mistake;", duration=2.5, fade_out=0., color=(50, 50, 100), force=True)  # 13.5
                TEXT.add("Unfortunately, Dad came and said :", duration=3.0, fade_out=0.0, color=(50, 50, 100), force=True)  # 16.5
                TEXT.add("\"Don't watch those who have failed.\"", duration=2.0, fade_out=0.0, color=(100, 50, 50), force=True)  # 18.5
                TEXT.add("\"They don't deserve.\"", duration=2.5, fade_out=2.5, color=(50, 50, 100), force=True)
            case 7:
                self.channel.play(Sound(join_path("data", "sounds", "phone_rec", f"7.ogg")))
                TEXT.replace("", duration=3.5, fade_out=0., color=(50, 50, 100), force=True)  # 3.5
                TEXT.add("TIC TAC", duration=2.5, fade_out=0., color=(50, 50, 100), force=True)  # 6.0
                TEXT.add("Seven hours passed.", duration=2.0, fade_out=3.0, color=(50, 50, 100), force=True)  # 11
                TEXT.add("Are you sleeping ?", duration=1.5, fade_out=0., color=(50, 50, 100), force=True)  # 12.5
                TEXT.add("Are you dreaming ?", duration=1.5, fade_out=0.0, color=(50, 50, 100), force=True)  # 14.0
                TEXT.add("You'd better to, she is coming.", duration=1.5, fade_out=0.0, color=(100, 50, 50), force=True)  # 15.5
                TEXT.add("Mom loves you;", duration=1.5, fade_out=0.0, color=(50, 50, 100), force=True)  # 17.0
                TEXT.add("She wants a hug.", duration=1.5, fade_out=0.0, color=(50, 50, 100), force=True)  # 18.0
                TEXT.add("Will you give it to her ?", duration=2.5, fade_out=2.5, color=(50, 50, 100), force=True)
            case 8:
                self.channel.play(Sound(join_path("data", "sounds", "phone_rec", f"8.ogg")))
                TEXT.replace("", duration=1.25, fade_out=0., color=(50, 50, 100), force=True)
                TEXT.add("TIC...", duration=1.75, fade_out=0., color=(50, 50, 100), force=True)  # 3.0
                TEXT.add("...TAC ", duration=1.75, fade_out=0., color=(50, 50, 100), force=True)  # 5.0
                TEXT.add("Eight hours passed.", duration=2.0, fade_out=1.75, color=(50, 50, 100), force=True)  # 8.5
                TEXT.add("His eyes don't see.", duration=2.75, fade_out=0., color=(50, 50, 100), force=True)  # 11.25
                TEXT.add("His ears spot you.", duration=2.75, fade_out=0., color=(50, 50, 100), force=True)  # 14.
                TEXT.add("Dad may be blind,", duration=3.0, fade_out=0., color=(50, 50, 100), force=True)  # 17.
                TEXT.add("But he still ears you.", duration=2.50, fade_out=2.5, color=(100, 50, 50), force=True)
            case 9:
                self.channel.play(Sound(join_path("data", "sounds", "phone_rec", f"9.ogg")))
            case hour:
                try:
                    self.channel.play(Sound(join_path("data", "sounds", "phone_rec", f"{hour}.ogg")))
                except FileNotFoundError:
                    print(f"File not found: {hour}.ogg")

    def update(self, player):
        self.timer += DISPLAY.delta_time

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

        if self.stopped_time:
            self.stopped_time = False
            GAME_LOGIC.time_stopped = False

        if GAME_LOGIC.phone_alert and int(self.timer * 1.8) % 2:
            if self.bip_sound.get_num_channels() == 0:
                self.bip_sound.set_volume(max(0., 1. - distance(player.pos, self.pos) / 7.))
                self.bip_sound.play()
            # {"z", "y", "z", "intensity", "red", "green", "blue", "direction_x", "direction_y", "direction_z", NULL};
            GAME_LOGIC.RAY_CASTER.add_light(
                *self.pos,
                0.6,
                0.9, 0.2, 0.3,
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
        self.sound: Sound = Sound(join_path("data", "sounds", "sfx", "plush_lost.ogg"))
        self.channel: Channel = Channel(2)
        set_stereo_volume(GAME_LOGIC.PLAYER, self.pos, self.channel)
        self.channel.play(self.sound)

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
        self.sound: Sound = Sound(join_path("data", "sounds", "sfx", "plush_found.ogg"))

    def can_interact(self, player) -> bool:
        if player.has_teddy_bear and player.is_looking_at(self.pos, 0.7) and distance(player.pos, self.pos) < 2.5:
            TEXT.replace("Give back the friend", duration=0.0, fade_out=0.3, color=(100, 100, 100))
            return True
        return False

    def interact(self, player):
        player.has_teddy_bear = False
        self.sound.play()
        GAME_LOGIC.monster_list['Mimic'].calm()  # type: ignore

    def update(self, player):
        ...


class Door(Interaction):
    def __init__(self, pos):
        self.image: Surface = load_image("data", "images", "props", "door.png")
        self.pos = pos
        self.angle: float = 0

        self.open_sound: Sound = Sound(join_path("data", "sounds", "sfx", "door_open.ogg"))
        self.close_sound: Sound = Sound(join_path("data", "sounds", "sfx", "door_close.ogg"))
        self.open_end_sound: Sound = Sound(join_path("data", "sounds", "sfx", "door_open_end.ogg"))

    def can_interact(self, player) -> bool:
        if player.is_looking_at((self.pos[0] - sin(radians(self.angle)) * 0.4, self.pos[1], self.pos[2] - cos(radians(self.angle)) * 0.4), 0.4) and distance(player.pos, self.pos) < 2.0:
            TEXT.replace("Close the door" if GAME_LOGIC.door_open else "Open the door", duration=0.0, fade_out=0.3, color=(100, 100, 100))
            return True
        return False

    def interact(self, player):
        GAME_LOGIC.door_open = not GAME_LOGIC.door_open

    def update(self, player):

        if GAME_LOGIC.door_open:
            if self.angle != 90:
                if self.angle == 0:
                    self.open_sound.play()
                self.angle = min(90., self.angle + DISPLAY.delta_time * 150)
                if self.angle == 90:
                    self.open_end_sound.play()
        elif self.angle != 0:
            self.angle = max(0., self.angle - DISPLAY.delta_time * 180)
            if self.angle == 0:
                self.close_sound.play()

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
        self.close: bool = False
        self.close_sound: Sound = Sound(join_path("data", "sounds", "sfx", "window_close.ogg"))
        self.wind_sound: Sound = Sound(join_path("data", "sounds", "sfx", "wind_and_crickets.ogg"))

        self.channel: Channel = Channel(3)
        set_stereo_volume(GAME_LOGIC.PLAYER, self.pos, self.channel, volume=0.0)
        self.channel.play(self.wind_sound, loops=-1)

    def can_interact(self, player) -> bool:
        if not self.y:
            return False

        if player.is_looking_at((self.pos[0], self.pos[1] + self.y, self.pos[2] - 0.4), 0.4) and distance(player.pos, self.pos) < 1.5:
            TEXT.replace("Close the window", duration=0.0, fade_out=0.3, color=(100, 100, 100))
            return True
        return False

    def interact(self, player):
        self.close = True

    def update(self, player):

        if self.close:
            self.y = max(0., self.y - DISPLAY.delta_time * 1.5)
            if not self.y:
                self.close = False
                self.close_sound.play()
        set_stereo_volume(player, self.pos, self.channel, volume=self.y * 2.3, hear_distance=9.)

        GAME_LOGIC.RAY_CASTER.add_surface(
            self.image,
            self.pos[0], self.pos[1] + 0.5 + self.y, self.pos[2] - 0.8,
            self.pos[0], self.pos[1] + self.y, self.pos[2],
            rm=True
        )
