from abc import ABC, abstractmethod

from random import randint, choice as random_choice
from math import cos, sin, atan2

from pygame.mixer import Sound, Channel
from pygame.surface import Surface

from scripts.visuals import VISUALS
from scripts.display import DISPLAY
from scripts.text import TEXT
from scripts.input_handler import INPUT
from scripts.game_logic import GAME_LOGIC
from scripts.game_over import GAME_OVER_SCREEN
from scripts.utils import load_image, add_surface_toward_player_2d, join_path, set_stereo_volume, distance_2d
from scripts.interactions import TeddyBear


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
        self.channel: Channel = Channel(4)
        self.danger_sound = Sound(join_path("data", "sounds", "sfx", "hangman_danger.ogg"))
        self.danger_channel: Channel = Channel(5)

    def update(self):
        """Update the monster each frame."""
        if not self.aggressiveness:
            return

        if self.state:
            self.y = max(0., self.y - DISPLAY.delta_time)
            set_stereo_volume(GAME_LOGIC.PLAYER, (self.x, 1, self.z), self.channel)
            if (GAME_LOGIC.PLAYER.use_flashlight or GAME_LOGIC.PLAYER.bedside_light) and GAME_LOGIC.PLAYER.is_looking_at((self.x, 1.4 + self.y, self.z), 1.5):
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
                self.madness = max(0., self.madness - DISPLAY.delta_time * 0.2)

            self.danger_channel.set_volume(self.madness)

            if self.madness > 1.0:
                GAME_OVER_SCREEN.reason = "Don't look at the hangman.\n" \
                                          "Listen carefully for the rope to know when he's coming."
                GAME_OVER_SCREEN.killer = "hangman"
                GAME_LOGIC.game_over()

        if GAME_LOGIC.time_stopped and not self.state:
            return

        self.timer -= DISPLAY.delta_time * randint(1, 3) / 3
        if self.timer <= 0:
            self.state = not self.state
            if self.state:
                self.timer = 10 + self.aggressiveness
                self.channel.play(self.rope_sound, loops=-1)
                self.danger_channel.set_volume(0, 0)
                self.danger_channel.play(self.danger_sound, loops=-1)

                self.x, self.z = GAME_LOGIC.PLAYER.x, GAME_LOGIC.PLAYER.z
                while distance_2d((self.x, 0.0, self.z), GAME_LOGIC.PLAYER.pos) < 1.5:
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
        # TODO: Sounds
        super().__init__()

        self.front_image: Surface = load_image("data", "images", "props", "chest_front.png")
        self.left_image: Surface = load_image("data", "images", "props", "chest_left.png")
        self.right_image: Surface = load_image("data", "images", "props", "chest_right.png")
        self.top_image1: Surface = load_image("data", "images", "props", "chest_top1.png")
        self.top_image2: Surface = load_image("data", "images", "props", "chest_top2.png")
        self.top_image3: Surface = load_image("data", "images", "props", "chest_top3.png")

        self.monster_image: Surface = load_image("data", "images", "monsters", "mimic.png")

        self.timer = 15.

        self.x: float = 0
        self.z: float = 0

        self.angle_y: float = 0

        self.teddy_bear: TeddyBear | None = None

    def update(self):
        """Update the monster each frame."""
        if not self.aggressiveness:
            return

        if self.state > 3:
            target = (
                GAME_LOGIC.PLAYER.pos
                if (not GAME_LOGIC.PLAYER.in_wardrobe or GAME_LOGIC.PLAYER.has_teddy_bear)
                else (
                    self.teddy_bear.pos if self.teddy_bear else (-2.2, 0.2, -0.3)
                )
            )

            # orient the monster toward the target
            self.angle_y = atan2(target[0] - self.x, target[2] - self.z)

            # move the monster toward the target
            self.x += sin(self.angle_y) * DISPLAY.delta_time * 2
            self.z += cos(self.angle_y) * DISPLAY.delta_time * 2

            if distance_2d((self.x, 0.0, self.z), target) < 1.0:
                if target == GAME_LOGIC.PLAYER.pos:
                    if GAME_LOGIC.PLAYER.in_wardrobe:
                        GAME_OVER_SCREEN.reason = "Steven was looking for his friend.\n" \
                                                  "If you found the plushie, give it back to him, don't hide yourself."
                    elif GAME_LOGIC.PLAYER.has_teddy_bear:
                        GAME_OVER_SCREEN.reason = "Steven was looking for his friend.\n" \
                                                  "If you found the plushie, give it back to him as soon as possible."
                    else:
                        GAME_OVER_SCREEN.reason = "Steven was looking for his friend.\n" \
                                                  "The plushie is hidden in the room. Find it before he gets angry.\n" \
                                                  "If you can't find the plushie, hide yourself in the wardrobe."
                    GAME_OVER_SCREEN.killer = "mimic"
                    GAME_LOGIC.game_over()
                elif self.teddy_bear:
                    GAME_LOGIC.interaction_list.remove(self.teddy_bear)
                    self.teddy_bear = None
                else:
                    self.calm()

        if GAME_LOGIC.time_stopped and self.state < 3:
            return

        self.timer -= DISPLAY.delta_time * (1 + self.aggressiveness / 10) * randint(1, 3) / 3
        if self.timer <= 0:
            self.state += 1
            match self.state:
                case 1:
                    self.timer = 10.
                    self.teddy_bear = TeddyBear()
                    GAME_LOGIC.interaction_list.insert(0, self.teddy_bear)
                case 2:
                    self.timer = 10.
                case 3:
                    self.timer = 5.
                    GAME_LOGIC.time_stopped = True
                case 4:
                    self.timer = 25.
                    self.x = -2.2
                    self.z = -0.3
                case _:
                    ...

    def calm(self):

        if self.state >= 3:
            GAME_LOGIC.time_stopped = False
        self.state = 0
        self.timer = 25.
        self.teddy_bear = None
        self.x = 0
        self.z = 0

    def draw(self):
        """Draw the monster each frame."""

        match self.state:
            case 0 | 1:
                self.draw_chest()

            case 2 | 3:  # phase last 10 seconds
                self.draw_chest()
                temp = max(0., 1.0 - self.timer / 10) if self.state == 2 else 1.0
                # {"z", "y", "z", "intensity", "red", "green", "blue", "direction_x", "direction_y", "direction_z", NULL};
                GAME_LOGIC.RAY_CASTER.add_light(
                    -2.2, 0.2, -0.3,
                    2.0 * temp,
                    1.0, 0.3, 0.0,
                )
                self.z = 0.02 * (int(self.timer * 100) % 2 - 0.5) * temp
                self.x = 0.016 * (int(self.timer * 100) % 2 - 0.5) * temp

            case _:
                GAME_LOGIC.RAY_CASTER.add_light(
                    self.x, 0.2, self.z,
                    2.0,
                    1.0, 0.3, 0.0,
                )
                add_surface_toward_player_2d(
                    GAME_LOGIC.RAY_CASTER,
                    GAME_LOGIC.PLAYER,
                    self.monster_image,
                    (self.x, 0, self.z),
                    1.5,
                    1.0,
                )

    def draw_chest(self):

        # {"image", "A_x", "A_y", "A_z", "B_x", "B_y", "B_z","C_x", "C_y", "C_z", "rm", NULL};
        GAME_LOGIC.RAY_CASTER.add_surface(
            self.front_image,
            -1.9 + self.x, 0.41, -0.95 + self.z,
            -1.9 + self.x, 0.0, 0.35 + self.z,
            rm=True,
        )
        GAME_LOGIC.RAY_CASTER.add_surface(
            self.left_image,
            -2.5 + self.x, 0.6, -0.95 + self.z,
            -1.9 + self.x, 0.0, -0.95 + self.z,
            rm=True,
        )
        GAME_LOGIC.RAY_CASTER.add_surface(
            self.right_image,
            -2.5 + self.x, 0.6, 0.35 + self.z,
            -1.9 + self.x, 0.0, 0.35 + self.z,
            rm=True,
        )
        GAME_LOGIC.RAY_CASTER.add_surface(
            self.top_image2,
            -2.31 + self.x, 0.6, -0.95 + self.z,
            -2.09 + self.x, 0.6, 0.35 + self.z,
            -2.09 + self.x, 0.6, -0.95 + self.z,
            rm=True,
        )

        GAME_LOGIC.RAY_CASTER.add_surface(
            self.top_image3,
            -2.1 + self.x, 0.6, -0.95 + self.z,
            -1.89 + self.x, 0.4, 0.35 + self.z,
            -1.89 + self.x, 0.4, -0.95 + self.z,
            rm=True,
        )

        GAME_LOGIC.RAY_CASTER.add_surface(
            self.top_image1,
            -2.3 + self.x, 0.6, -0.95 + self.z,
            -2.5 + self.x, 0.4, 0.35 + self.z,
            -2.5 + self.x, 0.4, -0.95 + self.z,
            rm=True,
        )


class Crawler(Monster):
    def __init__(self):
        super().__init__()
        self.hand_image: Surface = load_image("data", "images", "monsters", "crawler_hand.png")
        self.monster_image: Surface = load_image("data", "images", "monsters", "crawler.png")

        self.timer = 20.

        self.can_grab: bool = False
        self.grabbed: bool = False

        self.position = 0  # 0 == front_bed

        self.x = 0.0
        self.z = 0.0

        self.angle_y = 0.0

        self.channel: Channel = Channel(7)

        self.sound: Sound = Sound(join_path("data", "sounds", "sfx", "crawler.ogg"))

    def update(self):

        if not self.aggressiveness:
            return

        if self.state == 1:
            if self.z > 0:
                self.z = max(0., self.z - DISPLAY.delta_time * 0.1)
                return

            if self.grabbed:
                self.timer -= DISPLAY.delta_time
                if self.timer <= 0:
                    self.grabbed = False
                    self.timer = 3.
                    return
                VISUALS.shake = 1.0
                VISUALS.fish_eye = 1.0
                GAME_LOGIC.PLAYER.x = 0
                GAME_LOGIC.PLAYER.z = 0.3
                GAME_LOGIC.PLAYER.angle_y = 90
                GAME_LOGIC.PLAYER.angle_x = -90
                return

            if self.can_grab and not GAME_LOGIC.PLAYER.in_bed:
                if self.position == 0:
                    if distance_2d(GAME_LOGIC.PLAYER.pos, (0., 0., 1.5)) < 1.1:
                        self.grabbed = True
                        self.can_grab = False
                        self.timer = 5.
                        return
            else:
                self.timer -= DISPLAY.delta_time
                if self.timer <= 0:
                    self.can_grab = True
                    self.timer = 20.
                return

        elif self.state == 2:
            set_stereo_volume(GAME_LOGIC.PLAYER, (self.x, 0, self.z), self.channel)
            self.timer -= DISPLAY.delta_time
            if len(TEXT.text_list) < 2:
                TEXT.add(
                    " " * randint(0, 8) + "HIDE" + " " * randint(0, 8),
                    duration=0.08, fade_out=0., color=(50, 5, 5), font="HelpMe",
                    y=randint(50, DISPLAY.screen_size[1] - 50), size=32
                )
            VISUALS.fish_eye = 0.8
            if self.timer <= 0:
                self.timer = 1.0
                target = GAME_LOGIC.PLAYER.pos if not (GAME_LOGIC.PLAYER.in_wardrobe or GAME_LOGIC.PLAYER.in_bed) else (0, 0, 1.3)

                self.angle_y = atan2(target[0] - self.x, target[2] - self.z)

                self.x += sin(self.angle_y) * 0.5
                self.z += cos(self.angle_y) * 0.5

                if distance_2d((self.x, 0.0, self.z), target) < 1.0:
                    if GAME_LOGIC.PLAYER.in_wardrobe or GAME_LOGIC.PLAYER.in_bed:
                        self.state = 0
                        self.channel.stop()
                        self.timer = 20.
                        GAME_LOGIC.time_stopped = False
                    else:
                        GAME_OVER_SCREEN.reason = "The crawler is coming from under the bed.\n" \
                                                  "Hide in the closet or get on the bed.\n" \
                                                  "Pay attention to the sounds to know when he gets back under the bed."
                        GAME_OVER_SCREEN.killer = "crawler"
                        GAME_LOGIC.game_over()

        if GAME_LOGIC.time_stopped:
            return

        self.timer -= (
                DISPLAY.delta_time
                * (1 + self.aggressiveness / 10)
                * randint(1, 3) / 3
                * (0.5 * (GAME_LOGIC.PLAYER.use_flashlight + GAME_LOGIC.PLAYER.bedside_light * 2))
        )

        if self.timer <= 0:
            self.state += 1
            match self.state:
                case 1:
                    self.z = 0.5
                    self.can_grab = True
                    self.timer = 30.
                case 2:
                    self.channel.play(self.sound)
                    self.x = 0.
                    self.z = 1.3
                    self.timer = 2.5
                    GAME_LOGIC.time_stopped = True

    def draw(self):

        if not self.aggressiveness or not self.state:
            return

        match self.state:
            case 1:
                GAME_LOGIC.RAY_CASTER.add_surface(
                    self.hand_image,
                    -0.2 + (sin(self.timer * 2) / 20) * (not self.grabbed), 0.05, 1.52 + self.z,
                    0.2 + (sin(self.timer * 2) / 20) * (not self.grabbed), 0.2 + (sin(self.timer * 1.5) / 30) * (not self.grabbed), 1.0 + self.z,
                    -0.2 + (sin(self.timer * 2) / 20) * (not self.grabbed), 0.2 + (sin(self.timer * 1.5) / 30) * (not self.grabbed), 1.0 + self.z,
                    rm=True,
                )
            case 2:
                add_surface_toward_player_2d(
                    GAME_LOGIC.RAY_CASTER,
                    GAME_LOGIC.PLAYER,
                    self.monster_image,
                    (self.x, 0, self.z),
                    0.7,
                    0.7,
                )


class Guest(Monster):
    def __init__(self):
        super().__init__()

        self.timer = 20.

        self.x = 1.0
        self.state = 0
        self.running: bool = False

        self.eye_image: Surface = load_image("data", "images", "monsters", "guest_eye.png")
        self.running_image: Surface = load_image("data", "images", "monsters", "guest_running.png")

        self.scream_sound: Sound = Sound(join_path("data", "sounds", "sfx", "guest_scream.ogg"))

        self.door_hit_sound: Sound = Sound(join_path("data", "sounds", "sfx", "guest_door_hit.ogg"))

        self.lost_sound: Sound = Sound(join_path("data", "sounds", "sfx", "guest_lost.ogg"))
        self.breath_sound: Sound = Sound(join_path("data", "sounds", "sfx", "guest_breath.ogg"))

        self.channel: Channel = Channel(6)
        self.channel.set_volume(0., 0.)
        self.running_sound: Sound = Sound(join_path("data", "sounds", "sfx", "guest_running.ogg"))

    def update(self):
        if not self.aggressiveness or GAME_LOGIC.monster_list["Mom"].state or GAME_LOGIC.monster_list["Dad"].state:
            return

        match self.state:
            case 1:
                if GAME_LOGIC.door_open:
                    if self.channel.get_busy():
                        GAME_OVER_SCREEN.reason = "Don't open while the Guest is knocking the door."
                        GAME_OVER_SCREEN.killer = "guest"
                        GAME_LOGIC.game_over()
                        return
                    if GAME_LOGIC.PLAYER.use_flashlight:
                        if GAME_LOGIC.PLAYER.is_looking_at((7., 1., -0.8), 1.5):
                            if GAME_LOGIC.PLAYER.x > 1.2 and -1.6 < GAME_LOGIC.PLAYER.z < -0.4:
                                self.x -= DISPLAY.delta_time
                                if self.x <= 0:
                                    self.state = 0
                                    self.timer = 20.
                                return
                self.x = min(1.0, self.x + DISPLAY.delta_time)
            case 2:
                if self.running:
                    set_stereo_volume(GAME_LOGIC.PLAYER, (2.5 + self.x, 2.0, -0.8), self.channel)
                    self.x -= DISPLAY.delta_time * 2.5
                    if self.x <= 0:
                        self.channel.stop()
                        if not GAME_LOGIC.door_open:
                            self.channel.play(self.door_hit_sound)
                            self.state = 1
                            GAME_LOGIC.time_stopped = False
                            self.x = 1.0
                            self.timer = 20.
                            return
                        if GAME_LOGIC.PLAYER.in_wardrobe:
                            if GAME_LOGIC.PLAYER.use_flashlight:
                                GAME_OVER_SCREEN.reason = "The Guest saw your flashlight in the closet.\n" \
                                                          "While you're hiding, turn off all the lights.\n" \
                                                          "If you see him running, close the door as fast as you can."
                                GAME_OVER_SCREEN.killer = "guest"
                                GAME_LOGIC.game_over()
                                return
                            self.lost_sound.play()
                            self.timer = 20.
                            self.x = 4.5
                            self.running = False
                            GAME_LOGIC.time_stopped = False
                            return
                        GAME_OVER_SCREEN.reason = "When the Guest runs towards you, close the door as fast as you can.\n" \
                                                  "He will start running if the door is open and he sees a light.\n"
                        GAME_OVER_SCREEN.killer = "guest"
                        GAME_LOGIC.game_over()
                    return
                if GAME_LOGIC.door_open:
                    if GAME_LOGIC.PLAYER.use_flashlight or GAME_LOGIC.PLAYER.bedside_light:
                        if GAME_LOGIC.time_stopped:
                            self.state = 1
                            self.timer = 20.
                            return
                        self.running = True
                        self.channel.play(self.running_sound)
                        self.scream_sound.play()
                        GAME_LOGIC.time_stopped = True
                        return
            case 3:
                if GAME_LOGIC.door_open:
                    if GAME_LOGIC.PLAYER.use_flashlight or GAME_LOGIC.PLAYER.bedside_light:
                        if GAME_LOGIC.PLAYER.in_wardrobe:
                            if GAME_LOGIC.PLAYER.use_flashlight:
                                GAME_OVER_SCREEN.reason = "The Guest saw your flashlight in the closet.\n" \
                                                          "While you're hiding, turn off all the lights.\n" \
                                                          "Pay attention to the sounds to know when he leaves."
                                GAME_OVER_SCREEN.killer = "guest"
                                GAME_LOGIC.game_over()
                                return
                            self.lost_sound.play()
                            self.timer = 20.
                            self.x = 4.5
                            self.running = False
                            self.state = 2
                            return
                        GAME_OVER_SCREEN.reason = "The Guest was waiting at your door and saw a light.\n" \
                                                  "When you open the door, make sure you don't have any light on.\n" \
                                                  "Listen to his breathing to know if he's here.\n" \
                                                  "If you hear him, close the door and run to the closet.\n"
                        GAME_OVER_SCREEN.killer = "guest"
                        GAME_LOGIC.game_over()
                        return
                    if self.breath_sound.get_num_channels() == 0:
                        self.breath_sound.play()

        if GAME_LOGIC.time_stopped and self.state < 3:
            return

        self.timer -= (
                DISPLAY.delta_time
                * (1 + self.aggressiveness / 10)
                * randint(1, 3) / 3
                * (1 + GAME_LOGIC.door_open)
        )
        if self.timer <= 0:
            self.state += 1
            match self.state:
                case 1:
                    self.x = 0.1
                    self.timer = 20.
                case 2:
                    self.timer = 20.
                    self.x = 4.5
                    self.running = False
                case 3:
                    self.timer = 30.
                    GAME_LOGIC.time_stopped = True
                case 4:
                    GAME_LOGIC.door_open = True
                    if GAME_LOGIC.PLAYER.in_wardrobe:
                        if GAME_LOGIC.PLAYER.use_flashlight:
                            GAME_OVER_SCREEN.reason = "The Guest saw your flashlight in the closet.\n" \
                                                      "While you're hiding, turn off all the lights.\n" \
                                                      "Pay attention to the sounds to know when he leaves."
                            GAME_OVER_SCREEN.killer = "guest"
                            GAME_LOGIC.game_over()
                            return
                        self.lost_sound.play()
                        self.timer = 20.
                        self.x = 4.5
                        self.running = False
                        self.state = 2
                        GAME_LOGIC.time_stopped = False
                        return
                    GAME_OVER_SCREEN.reason = "The Guest will try to come to your room by the door.\n" \
                                              "If you hide in the closet, he won't find you.\n" \
                                              "You can know if he is at the door by listening to his breathing.\n" \
                                              "But don't light up the room while he is at the door."
                    GAME_OVER_SCREEN.killer = "guest"
                    GAME_LOGIC.game_over()

    def draw(self):
        if (not self.aggressiveness or not self.state) or GAME_LOGIC.monster_list["Mom"].state:
            return

        match self.state:
            case 1:
                GAME_LOGIC.RAY_CASTER.add_surface(
                    self.eye_image,
                    8.0 - self.x, 2.0, -0.2,
                    8.0 - self.x, 0.0, -1.4,
                    rm=True,
                )
            case 2:
                if self.running:
                    GAME_LOGIC.RAY_CASTER.add_surface(
                        self.running_image,
                        2.5 + self.x, 2.0, -0.2,
                        2.5 + self.x, 0.0, -1.4,
                        rm=True,
                    )
                else:
                    GAME_LOGIC.RAY_CASTER.add_surface(
                        self.eye_image,
                        7.0, 2.0, -0.2,
                        7.0, 0.0, -1.4,
                        rm=True,
                    )


class Mom(Monster):
    def __init__(self):
        super().__init__()
        self.door = None
        self.state = False
        self.light: bool = False
        self.timer = 50.
        self.angriness: float = 0.

        self.open_door_sound: Sound = Sound(join_path('data', 'sounds', 'sfx', 'door_open_fast.ogg'))
        self.light_sound: Sound = Sound(join_path('data', 'sounds', 'sfx', 'corridor_click.ogg'))

    def update(self):
        if not self.aggressiveness:
            return

        if self.state:
            GAME_LOGIC.door_open = True

            if not self.light:
                self.timer -= DISPLAY.delta_time
                if self.timer <= 0:
                    self.timer = 10.
                    self.light = True
                    self.light_sound.play()
                return

            if not GAME_LOGIC.PLAYER.in_bed:
                GAME_OVER_SCREEN.reason = "Mom saw you were not in bed.\n" \
                                          "When you hear her coming, turn the lights off and pretend you're sleeping."
                self.angriness += DISPLAY.delta_time * 0.1 * (1 + self.aggressiveness / 10)
            elif GAME_LOGIC.PLAYER.use_flashlight or GAME_LOGIC.PLAYER.bedside_light:
                GAME_OVER_SCREEN.reason = "Mom saw a light.\n" \
                                          "When you hear her coming, turn the lights off and pretend you're sleeping."
                self.angriness += DISPLAY.delta_time * 0.1 * (1 + self.aggressiveness / 10)
            else:
                self.angriness = max(0., self.angriness - DISPLAY.delta_time * 0.1)

            VISUALS.fish_eye = self.angriness + VISUALS.min_fish_eye
            VISUALS.vignette = self.angriness + VISUALS.min_vignette
            #TODO: sound mom angry
            if len(TEXT.text_list) < 2:
                TEXT.add(
                    " " * randint(0, 5) + "GO TO BED" + " " * randint(0, 5),
                    duration=0.08, fade_out=0., color=(60, 5, 5), font="HelpMe",
                    y=randint(50, DISPLAY.screen_size[1] - 50), size=int(32 * (1 + self.angriness))
                )

            if self.angriness > 1.0:
                GAME_OVER_SCREEN.killer = "mom"
                GAME_LOGIC.game_over()

            self.timer -= DISPLAY.delta_time

        if self.timer <= 0:
            self.state = not self.state
            if self.state:
                GAME_LOGIC.time_stopped = True
                self.angriness = 0.
                self.timer = 1.
                self.door.angle = 90.
                self.light = False
                if not GAME_LOGIC.door_open:
                    self.open_door_sound.play()
                # TODO: sound mom
            else:
                GAME_LOGIC.time_stopped = False
                self.timer = 50.
                self.light_sound.play()

        if GAME_LOGIC.time_stopped:
            return

        self.timer -= (
                DISPLAY.delta_time
                * (1 + self.aggressiveness / 10)
                * randint(1, 3) / 3
        )

    def draw(self):
        if self.state:
            if self.light:
                GAME_LOGIC.RAY_CASTER.add_light(
                    2.5, 2.0, -1.0,
                    5.0,
                    1.0, 1.0, 0.5,
                    -2.5, 0.0, -1.0,
                )


class Dad(Monster):
    def __init__(self):
        super().__init__()
        self.door = None
        self.state = False
        self.timer = 40.
        self.angriness: float = 0.
        self.light: bool = False

        self.open_door_sound: Sound = Sound(join_path('data', 'sounds', 'sfx', 'door_open_fast.ogg'))
        self.light_sound: Sound = Sound(join_path('data', 'sounds', 'sfx', 'corridor_click.ogg'))

    def update(self):
        if not self.aggressiveness:
            return

        if self.state:
            GAME_LOGIC.door_open = True

            if not self.light:
                self.timer -= DISPLAY.delta_time
                if self.timer <= 0:
                    self.timer = 15.
                    self.light = True
                    self.light_sound.play()
                return

            if not GAME_LOGIC.PLAYER.in_wardrobe and (INPUT.jump() or INPUT.left() or INPUT.right() or INPUT.up() or INPUT.down()):
                self.angriness += DISPLAY.delta_time * 0.2 * (1 + self.aggressiveness / 5)
                if len(TEXT.text_list) < 2:
                    TEXT.add(
                        " " * randint(0, 5) + "I HEAR YOU" + " " * randint(0, 5),
                        duration=0.08, fade_out=0., color=(70, 5, 5), font="HelpMe",
                        y=randint(50, DISPLAY.screen_size[1] - 50), size=int(32 * (1 + self.angriness))
                    )
                # TODO: sound dad angry

            VISUALS.shake = self.angriness + VISUALS.min_shake
            VISUALS.distortion = self.angriness + VISUALS.min_distortion

            if self.angriness > 1.0:
                GAME_OVER_SCREEN.reason = "Dad will get angry if you move.\n" \
                                          "You can move your head, but don't walk or jump."
                GAME_OVER_SCREEN.killer = "dad"
                GAME_LOGIC.game_over()

            self.timer -= DISPLAY.delta_time

        if self.timer <= 0:
            self.state = not self.state
            if self.state:
                GAME_LOGIC.time_stopped = True
                self.angriness = 0.
                self.timer = 1.
                self.door.angle = 90.
                self.light = False
                if not GAME_LOGIC.door_open:
                    self.open_door_sound.play()
                # TODO: sound dad
            else:
                GAME_LOGIC.time_stopped = False
                self.timer = 60.
                self.light_sound.play()

        if GAME_LOGIC.time_stopped:
            return

        self.timer -= (
                DISPLAY.delta_time
                * (1 + self.aggressiveness / 10)
                * randint(1, 3) / 3
        )

    def draw(self):
        if self.state:
            if self.light:
                GAME_LOGIC.RAY_CASTER.add_light(
                    2.5, 2.0, -1.0,
                    5.0,
                    1.0, 0.0, 0.0,
                    -2.5, 0.0, -1.0,
                )


class Watcher(Monster):
    def __init__(self):
        super().__init__()
        self.timer = 20.
        self.state = 0
        self.fear: float = 0.

        self.looking_image = load_image("data", "images", "monsters", "watcher_looking.png")
        self.inside_image = load_image("data", "images", "monsters", "watcher_inside.png")

        self.breath_sound: Sound = Sound(join_path('data', 'sounds', 'sfx', 'watcher_breath.ogg'))
        self.scared_sound: Sound = Sound(join_path('data', 'sounds', 'sfx', 'bed.ogg'))

    def update(self):
        if not self.aggressiveness or GAME_LOGIC.watcher_caught:
            return

        if self.state == 1 or self.state == 2:
            if GAME_LOGIC.PLAYER.in_wardrobe:
                if self.breath_sound.get_num_channels() == 0:
                    self.breath_sound.play()
            else:
                pos = (-1.2, 1.4, -3.37) if self.state == 1 else (-0.4, 1.4, -3.37)
                if GAME_LOGIC.PLAYER.use_flashlight and GAME_LOGIC.PLAYER.is_looking_at(pos, 0.6) and distance_2d(GAME_LOGIC.PLAYER.pos, pos) < 3.0:
                    self.fear += DISPLAY.delta_time * (1 - 0.5 * (self.state == 2))
                    VISUALS.shake += 1.5 * DISPLAY.delta_time
                    VISUALS.distortion += 1.5 * DISPLAY.delta_time
                    if self.fear >= 1.0:
                        self.scared_sound.play()
                        self.state = 0
                        self.timer = 20.
                    return
                else:
                    self.fear = max(0., self.fear - DISPLAY.delta_time)
        elif self.state == 3:
            if GAME_LOGIC.PLAYER.in_wardrobe:
                GAME_LOGIC.watcher_caught = True
                GAME_LOGIC.time_stopped = True
                GAME_OVER_SCREEN.reason = "You went to the wardrobe with the Watcher inside.\n" \
                                          "Use your light if you see his eyes to make him leave.\n" \
                                          "If you don't force him to leave fast enough, he will stay forever."
                GAME_OVER_SCREEN.killer = "watcher_hands"
                return

        if GAME_LOGIC.time_stopped:
            return

        if self.state < 3 or GAME_LOGIC.wardrobe_open:
            self.timer -= (
                    DISPLAY.delta_time
                    * (1 + self.aggressiveness / 10)
                    * randint(1, 4) / 4
                    * (1 + GAME_LOGIC.wardrobe_open)
            )
        elif self.state == 3:
            self.timer = 10.
            return

        if self.timer <= 0:
            self.state += 1
            match self.state:
                case 1:
                    self.fear = 0.
                    self.timer = 25.
                    #TODO: sound watcher moving
                case 2:
                    self.timer = 30.
                    self.fear = 0.
                    #TODO: sound watcher moving
                case 3:
                    #TODO: sound watcher moving
                    self.timer = 10.
                    if GAME_LOGIC.PLAYER.in_wardrobe:
                        GAME_LOGIC.watcher_caught = True
                        GAME_LOGIC.time_stopped = True
                        GAME_OVER_SCREEN.reason = "The Watcher caught you in the wardrobe.\n" \
                                                  "Leave the wardrobe if you hear his breath.\n" \
                                                  "Use your light if you see his eyes to make him leave.\n" \
                                                  "If you don't force him to leave fast enough, he will stay forever."
                        GAME_OVER_SCREEN.killer = "watcher_hands"
                        return
                case 4:
                    GAME_OVER_SCREEN.reason = "The Watcher will try to sneak out of the wardrobe.\n" \
                                              "If the door is open, he will get out.\n" \
                                              "Use your light if you see his eyes to make him leave.\n" \
                                              "If you don't force him to leave fast enough, he will stay forever."
                    GAME_OVER_SCREEN.killer = "watcher"
                    GAME_LOGIC.game_over()
                    return

    def draw(self):
        match self.state:
            case 1:
                if GAME_LOGIC.PLAYER.use_flashlight:
                    add_surface_toward_player_2d(
                        GAME_LOGIC.RAY_CASTER,
                        GAME_LOGIC.PLAYER,
                        self.looking_image,
                        (-1.2, 0.0, -3.37),
                        0.8, 2.0
                    )

            case 2:
                if GAME_LOGIC.PLAYER.use_flashlight or GAME_LOGIC.wardrobe_open:
                    add_surface_toward_player_2d(
                        GAME_LOGIC.RAY_CASTER,
                        GAME_LOGIC.PLAYER,
                        self.looking_image,
                        (-0.4, 0.0, -3.37),
                        0.8, 2.0
                    )

            case 3:
                if GAME_LOGIC.wardrobe_open and GAME_LOGIC.PLAYER.use_flashlight:
                    GAME_LOGIC.RAY_CASTER.add_surface(
                        self.inside_image,
                        -0.0, 2.0, -3.45,
                        -0.8, 0.0, -3.45,
                        rm=True,
                    )
                else:
                    add_surface_toward_player_2d(
                        GAME_LOGIC.RAY_CASTER,
                        GAME_LOGIC.PLAYER,
                        self.looking_image,
                        (-0.4, 0.0, -3.37),
                        0.8, 2.0
                    )


class Eye(Monster):
    def __init__(self):
        super().__init__()
        self.timer = 10.

        self.x = 8.
        self.state = 0.0
        self.window = None

        self.fear: float = 0.

        self.image = load_image("data", "images", "monsters", "Eye_in_the_night.png")
        self.dark_image = load_image("data", "images", "monsters", "Eye_in_the_night_2.png")
        self.eyes_image: tuple[Surface, ...] = (
            load_image("data", "images", "monsters", "Eye_1.png"),
            load_image("data", "images", "monsters", "Eye_2.png"),
            load_image("data", "images", "monsters", "Eye_3.png"),
        )

        self.scared_sound: Sound = Sound(join_path('data', 'sounds', 'sfx', 'eye_scared.ogg'))
        self.chanel: Channel = Channel(8)

    def update(self):
        if not self.aggressiveness:
            return

        self.chanel.set_volume(self.fear)
        if (self.state
                and GAME_LOGIC.PLAYER.use_flashlight
                and GAME_LOGIC.PLAYER.is_looking_at((2.8 + self.x, 1.0, 1.6))
                and GAME_LOGIC.PLAYER.x > 1.0
                and GAME_LOGIC.PLAYER.z > 1.0
                and self.x < 2.0):
            self.fear += DISPLAY.delta_time * (1 - self.aggressiveness / 25)
            VISUALS.shake = self.fear
            VISUALS.vignette = self.fear
            if self.fear >= 1.0:
                # TODO: sound eye caught
                self.state = 0
                self.chanel.stop()
                self.timer = 10.
            return
        self.fear = max(0., self.fear - DISPLAY.delta_time)

        if GAME_LOGIC.time_stopped:
            return

        if not self.state:
            self.timer -= (DISPLAY.delta_time
                           * (1 + self.aggressiveness / 10)
                           * randint(1, 4) / 4
                           * (0.5 * (GAME_LOGIC.PLAYER.use_flashlight + GAME_LOGIC.PLAYER.bedside_light * 2)))
            if self.timer <= 0:
                # TODO: sound eye wisper
                self.state = True
                self.chanel.set_volume(0)
                self.chanel.play(self.scared_sound, loops=-1)
                self.fear = 0.
                self.x = 8.
            return

        if self.x > 0:
            self.x -= (DISPLAY.delta_time * 0.5
                       * (1 + self.aggressiveness / 10)
                       * (0.5 * (GAME_LOGIC.PLAYER.use_flashlight + GAME_LOGIC.PLAYER.bedside_light * 2)))
            if self.x <= 0:
                self.x = 0
                #TODO: sound eye knock window
            return

        if self.window.y < 0.5:
            self.window.y += DISPLAY.delta_time * 0.015
            return

        GAME_OVER_SCREEN.reason = "The Eye in the night got you.\n" \
                                  "You must not let him open the window.\n" \
                                  "Use the flashlight to make him leave, then close the window."
        GAME_OVER_SCREEN.killer = "eye"
        GAME_LOGIC.game_over()

    def draw(self):
        if not self.aggressiveness or not self.state:
            return

        if GAME_LOGIC.PLAYER.use_flashlight:
            temp = self.image.copy()
            temp.blit(self.eyes_image[min(2, int(self.fear / 0.3))], (randint(-5, 5) * self.fear, randint(-2, 2) * self.fear))
            add_surface_toward_player_2d(
                GAME_LOGIC.RAY_CASTER,
                GAME_LOGIC.PLAYER,
                temp,
                (2.8 + self.x, 0.0, 1.6),
                0.8, 2.0
            )
            return

        add_surface_toward_player_2d(
            GAME_LOGIC.RAY_CASTER,
            GAME_LOGIC.PLAYER,
            self.dark_image,
            (2.8 + self.x, 0.0, 1.6),
            0.8, 2.0
        )


class Hallucination(Monster):
    def __init__(self):
        super().__init__()
        self.timer = 20.
        self.sounds: tuple[Sound, ...] = (
            Sound(join_path('data', 'sounds', 'phone_rec', 'chuchotage.ogg')),
            Sound(join_path('data', 'sounds', 'phone_rec', 'chuchotement_eyen_in_da_night.ogg')),
            Sound(join_path('data', 'sounds', 'phone_rec', 'hes_missing_goerges.ogg')),
            Sound(join_path('data', 'sounds', 'phone_rec', 'hes_watching_seeyou.ogg')),
        )

    def update(self):
        if not self.aggressiveness:
            return

        self.timer -= DISPLAY.delta_time * randint(0, 2)
        if self.timer <= 0.:
            self.timer = 25. - self.aggressiveness
            match randint(0, 3):
                case 0:
                    VISUALS.madness += 0.03
                    return

                case 1:
                    sound = random_choice(self.sounds)
                    sound.set_volume(randint(1, 5) / 10)
                    sound.play()
                    return

                case 2:
                    random_choice(list(GAME_LOGIC.monster_list.values())).timer -= 0.2
                    return

                case 3:
                    random_choice(list(GAME_LOGIC.monster_list.values())).aggressiveness += 1
                    return

    def draw(self):
        ...
