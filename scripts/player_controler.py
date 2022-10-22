from math import sin, cos, radians

from scripts.display import DISPLAY
from scripts.input_handler import INPUT


class Player:
    def __init__(self):
        self.x: float = 0
        self.y: float = 0
        self.z: float = 0

        self.angle_x: float = 0
        self.angle_y: float = 90

        self.walk_speed: float = 1.1
        self.run_speed: float = 1.6
        self.height: float = 1.3

        self._jump_speed: float = 0

        self.gravity: float = 2.2

        self.have_flashlight: bool = False
        self.use_flashlight: bool = True

    def update(self):

        self.angle_y -= INPUT.rel[0] * DISPLAY.delta_time
        self.angle_x = max(-90., min(90., self.angle_x - INPUT.rel[1] * DISPLAY.delta_time))

        speed = self.run_speed if INPUT.sprint() else self.walk_speed

        if INPUT.up():
            self.x += speed * cos(radians(self.angle_y)) * DISPLAY.delta_time
            self.z += speed * sin(radians(self.angle_y)) * DISPLAY.delta_time

        elif INPUT.down():
            self.x -= speed * cos(radians(self.angle_y)) * DISPLAY.delta_time
            self.z -= speed * sin(radians(self.angle_y)) * DISPLAY.delta_time

        if INPUT.left():
            self.x += speed * cos(radians(self.angle_y + 90)) * DISPLAY.delta_time
            self.z += speed * sin(radians(self.angle_y + 90)) * DISPLAY.delta_time

        elif INPUT.right():
            self.x -= speed * cos(radians(self.angle_y + 90)) * DISPLAY.delta_time
            self.z -= speed * sin(radians(self.angle_y + 90)) * DISPLAY.delta_time

        if INPUT.jump() and self.y <= 0:
            self._jump_speed = 0.6

        if self._jump_speed > 0 or self.y > 0:
            self.y += self._jump_speed * DISPLAY.delta_time
            self._jump_speed -= DISPLAY.delta_time * self.gravity

        if self.y < 0:
            self.y = 0
            self._jump_speed = 0
