from abc import ABC, abstractmethod

from random import randint
from math import cos, sin, atan2

from pygame.mixer import Sound, Channel
from pygame.surface import Surface

from scripts.visuals import VISUALS
from scripts.display import DISPLAY
from scripts.text import TEXT
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
        self.channel: Channel = Channel(2)
        self.danger_sound = Sound(join_path("data", "sounds", "sfx", "hangman_danger.ogg"))
        self.danger_channel: Channel = Channel(3)

    def update(self):
        """Update the monster each frame."""
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
                self.madness = max(0., self.madness - DISPLAY.delta_time * 0.2)

            self.danger_channel.set_volume(self.madness)

            if self.madness > 1.0:
                GAME_OVER_SCREEN.reason = "Don't look at the hangman. Listen carefully for the rope."
                GAME_OVER_SCREEN.killer = "hangman"
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
        super().__init__()

        self.front_image: Surface = load_image("data", "images", "props", "chest_front.png")
        self.side_image: Surface = load_image("data", "images", "props", "chest_side.png")
        self.top_image: Surface = load_image("data", "images", "props", "chest_top.png")

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
                        GAME_OVER_SCREEN.reason = "Don't hide if you found the plushie."
                    elif GAME_LOGIC.PLAYER.has_teddy_bear:
                        GAME_OVER_SCREEN.reason = "You must give back George before his friends gets angry."
                    else:
                        GAME_OVER_SCREEN.reason = "The plushie is hidden in the room. Find it before he gets angry."
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
                    GAME_LOGIC.interaction_list.append(self.teddy_bear)
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
            self.side_image,
            -2.5 + self.x, 0.6, -0.95 + self.z,
            -1.9 + self.x, 0.0, -0.95 + self.z,
            rm=True,
        )
        GAME_LOGIC.RAY_CASTER.add_surface(
            self.side_image,
            -2.5 + self.x, 0.6, 0.35 + self.z,
            -1.9 + self.x, 0.0, 0.35 + self.z,
            rm=True,
        )
        GAME_LOGIC.RAY_CASTER.add_surface(
            self.top_image,
            -2.31 + self.x, 0.6, -0.95 + self.z,
            -2.09 + self.x, 0.6, 0.35 + self.z,
            -2.09 + self.x, 0.6, -0.95 + self.z,
            rm=True,
        )

        GAME_LOGIC.RAY_CASTER.add_surface(
            self.top_image,
            -2.1 + self.x, 0.6, -0.95 + self.z,
            -1.89 + self.x, 0.4, 0.35 + self.z,
            -1.89 + self.x, 0.4, -0.95 + self.z,
            rm=True,
        )

        GAME_LOGIC.RAY_CASTER.add_surface(
            self.top_image,
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

            if self.can_grab:
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
            self.timer -= DISPLAY.delta_time
            if self.timer <= 0:
                self.timer = 1.0
                target = GAME_LOGIC.PLAYER.pos if not (GAME_LOGIC.PLAYER.in_wardrobe or GAME_LOGIC.PLAYER.in_bed) else (0, 0, 1.3)

                self.angle_y = atan2(target[0] - self.x, target[2] - self.z)

                self.x += sin(self.angle_y) * 0.5
                self.z += cos(self.angle_y) * 0.5

                if distance_2d((self.x, 0.0, self.z), target) < 1.0:
                    if GAME_LOGIC.PLAYER.in_wardrobe or GAME_LOGIC.PLAYER.in_bed:
                        self.state = 0
                        self.timer = 20.
                        GAME_LOGIC.time_stopped = False
                    else:
                        GAME_OVER_SCREEN.reason = "When the crawler is coming for you, get in the bed or in the wardrobe."
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
                    #TODO: sounds
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

        self.x = 1.0
        self.state = 1
        self.aggressiveness = 20

        self.eye_image: Surface = load_image("data", "images", "monsters", "guest_eye.png")
        self.running_image: Surface = load_image("data", "images", "monsters", "guest_running.png")

    def update(self):
        pass

    def draw(self):
        if not self.aggressiveness or not self.state:
            return

        match self.state:
            case 1:
                GAME_LOGIC.RAY_CASTER.add_surface(
                    self.eye_image,
                    8.0 - self.x, 2.0, -0.2,
                    8.0 - self.x, 0.0, -1.4,
                    rm=True,
                )


