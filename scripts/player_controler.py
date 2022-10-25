from math import sin, cos, radians

from pygame import Rect
from pygame.mixer import Sound

from scripts.display import DISPLAY
from scripts.input_handler import INPUT
from scripts.utils import MAP_COLLISIONS
from scripts.utils import line_point_distance, join_path


class Player:
    def __init__(self):
        self.x: float = 1.0
        self.y: float = 0
        self.z: float = 2.5

        self.angle_x: float = 0
        self.angle_y: float = 90

        self.walk_speed: float = 0.9
        self.run_speed: float = 1.6
        self.height: float = 1.3

        self._jump_speed: float = 0

        self.gravity: float = 2.2

        self.has_flashlight: bool = False
        self.use_flashlight: bool = False
        self.has_teddy_bear: bool = False

        self.bedside_light: bool = False

        self.in_bed: bool = False
        self.in_wardrobe: bool = False

        self.look_direction: tuple[float, float, float] = (0, 0, 0)

        self.cancel: tuple[float, float] = (0, 0)

        self.flashlight_sound = Sound(join_path("data", "sounds", "sfx", "flashlight.ogg"))
        self.steps_sound: tuple[Sound, Sound] = (
            Sound(join_path("data", "sounds", "sfx", "step1.ogg")),
            Sound(join_path("data", "sounds", "sfx", "step2.ogg"))
        )
        self.step_count: int = 0
        self.step_wait: float = 0.

        self.moved: bool = False

    @property
    def pos(self) -> tuple[float, float, float]:
        return self.x, self.y + self.height, self.z

    def collision(self):
        if Rect(int(self.x * 10), int(self.z * 10), 5, 5).collidelist(MAP_COLLISIONS) != -1:
            self.x, self.z = self.cancel
            return
        self.cancel = self.x, self.z
        self.moved = True

    def update(self):

        # print(self.z, self.z)

        if self.has_flashlight:
            if INPUT.flash_light():
                self.flashlight_sound.stop()
                self.flashlight_sound.play()
                self.use_flashlight = not self.use_flashlight

        if self.in_bed or self.in_wardrobe:
            if INPUT.jump() or INPUT.interact():
                self.in_bed = self.in_wardrobe = False
            return

        self.angle_y -= INPUT.rel[0] * DISPLAY.delta_time
        self.angle_x = max(-90., min(90., self.angle_x - INPUT.rel[1] * DISPLAY.delta_time))

        speed = self.run_speed if INPUT.sprint() else self.walk_speed

        self.cancel = self.x, self.z
        self.moved = False

        if INPUT.up():
            self.x += speed * cos(radians(self.angle_y)) * DISPLAY.delta_time
            self.collision()
            self.z += speed * sin(radians(self.angle_y)) * DISPLAY.delta_time
            self.collision()

        elif INPUT.down():
            self.x -= speed * cos(radians(self.angle_y)) * DISPLAY.delta_time
            self.collision()
            self.z -= speed * sin(radians(self.angle_y)) * DISPLAY.delta_time
            self.collision()

        if INPUT.left():
            self.x += speed * cos(radians(self.angle_y + 90)) * DISPLAY.delta_time
            self.collision()
            self.z += speed * sin(radians(self.angle_y + 90)) * DISPLAY.delta_time
            self.collision()

        elif INPUT.right():
            self.x -= speed * cos(radians(self.angle_y + 90)) * DISPLAY.delta_time
            self.collision()
            self.z -= speed * sin(radians(self.angle_y + 90)) * DISPLAY.delta_time
            self.collision()

        if self.y > 0:
            self.step_wait = 0.
        elif self.moved:
            self.step_wait -= DISPLAY.delta_time
            if self.step_wait <= 0:
                self.step_wait = 0.5 if INPUT.sprint() else 0.7
                self.step_count = (self.step_count + 1) % 2
                if self.steps_sound[self.step_count].get_num_channels() == 0:
                    self.steps_sound[self.step_count].play()

        # self.collision()

        if INPUT.jump() and self.y <= 0:
            self._jump_speed = 0.6

        if self._jump_speed > 0 or self.y > 0:
            self.y += self._jump_speed * DISPLAY.delta_time
            self._jump_speed -= DISPLAY.delta_time * self.gravity

        if self.y < 0:
            self.y = 0
            self._jump_speed = 0

        self.look_direction = (
            cos(radians(self.angle_y)),
            sin(radians(self.angle_x)),
            sin(radians(self.angle_y))
        )

    def is_looking_at(self, pos: tuple[float, float, float], error_dist: float = 0.8) -> bool:
        dist = line_point_distance(pos, self.pos, self.look_direction)
        return dist < error_dist
