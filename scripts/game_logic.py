from math import sin, cos, radians

from pygame import Surface

from scripts.player_controler import Player
from scripts.display import DISPLAY
from scripts.text import TEXT
from scripts.surface_loader import load_static_surfaces

from nostalgiaeraycasting import RayCaster


class GAME_LOGIC:
    HOUR_DURATION: float = 120.

    PLAYER: Player
    RAY_CASTER: RayCaster
    SURFACE: Surface

    hour: int
    remaining_time: float
    time_stopped: bool

    @classmethod
    def reset(cls):
        cls.PLAYER = Player()
        cls.RAY_CASTER = RayCaster()
        cls.SURFACE = Surface((128, 72))  # 16:9

        load_static_surfaces(cls.RAY_CASTER)

        hour = 0
        remaining_time = cls.HOUR_DURATION
        time_stopped = False

    @classmethod
    def update(cls) -> None:

        cls.PLAYER.update()

        if not cls.time_stopped:
            cls.remaining_time -= DISPLAY.delta_time
            if cls.remaining_time <= 0:
                cls.hour += 1
                cls.remaining_time = cls.HOUR_DURATION

        cls.display()

    @classmethod
    def display(cls) -> None:

        cls.SURFACE.fill((0, 0, 0))

        cls.RAY_CASTER.clear_lights()
        # {"x", "y", "z", "intensity", "red", "green", "blue", "direction_x", "direction_y", "direction_z", NULL};
        cls.RAY_CASTER.add_light(
            cls.PLAYER.x, cls.PLAYER.height, cls.PLAYER.z,
            3.,
            0.15, 0.07, 0.05,
        )
        if cls.PLAYER.use_flashlight:
            cls.RAY_CASTER.add_light(
                cls.PLAYER.x, cls.PLAYER.y + cls.PLAYER.height, cls.PLAYER.z,
                DISPLAY.VIEW_DISTANCE, 0.5, 0.6, 0.7,
                direction_x=cls.PLAYER.x + cos(radians(cls.PLAYER.angle_y)) * DISPLAY.VIEW_DISTANCE * 1.8,
                direction_y=cls.PLAYER.y + cls.PLAYER.height + sin(radians(cls.PLAYER.angle_x)) * DISPLAY.VIEW_DISTANCE * 1.8,
                direction_z=cls.PLAYER.z + sin(radians(cls.PLAYER.angle_y)) * DISPLAY.VIEW_DISTANCE * 1.8,
                )

        # {"dst_surface", "x", "y", "z", "angle_x", "angle_y", "fov", "view_distance", "rad", NULL};
        cls.RAY_CASTER.raycasting(
            cls.SURFACE,
            cls.PLAYER.x,
            cls.PLAYER.y + cls.PLAYER.height,
            cls.PLAYER.z,
            cls.PLAYER.angle_x,
            cls.PLAYER.angle_y,
            DISPLAY.FOV,
            DISPLAY.VIEW_DISTANCE,
        )

        DISPLAY.display_scaled(cls.SURFACE)
        TEXT.update()
