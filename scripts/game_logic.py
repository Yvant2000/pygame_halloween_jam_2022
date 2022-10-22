from pygame import Surface

from scripts.player_controler import Player
from scripts.display import DISPLAY
from scripts.utils import load_image, repeat_texture

from nostalgiaeraycasting import RayCaster


class GAME_LOGIC:
    PLAYER: Player
    RAY_CASTER: RayCaster
    SURFACE: Surface

    @classmethod
    def reset(cls):
        cls.PLAYER = Player()
        cls.RAY_CASTER = RayCaster()
        cls.SURFACE = Surface((128, 72))  # 16:9

        cls.load_static_surfaces()

    @classmethod
    def load_static_surfaces(cls):
        caster = cls.RAY_CASTER

        wall_texture = load_image("data", "images", "textures", "wall_texture.png")

        # {"image", "A_x", "A_y", "A_z", "B_x", "B_y", "B_z","C_x", "C_y", "C_z", "rm", NULL};
        caster.add_surface(
            repeat_texture(wall_texture, 5, 3),
            -2, 3, 4,
            3, 0, 4,
        )
        caster.add_surface(
            repeat_texture(wall_texture, 7, 3),
            -2, 3, -3,
            -2, 0, 4,
        )
        caster.add_surface(
            repeat_texture(wall_texture, 7, 3),
            3, 3, 4,
            3, 0, -3,
        )
        caster.add_surface(
            repeat_texture(wall_texture, 5, 3),
            3, 3, -3,
            -2, 0, -3,
        )

        caster.add_surface(
            repeat_texture(load_image("data", "images", "textures", "ground_texture.png"), 5, 7),
            3.05, 0, -3.05,
            -2.05, 0, 4.05,
            3.05, 0, 4.05,
        )
        caster.add_surface(
            repeat_texture(load_image("data", "images", "textures", "ceiling_texture.png"), 5, 7),
            3.05, 3, 4.05,
            -2.05, 3.01, -3.05,
            3.05, 3.01, -3.05,
        )

    @classmethod
    def update(cls) -> None:

        cls.PLAYER.update()

        cls.SURFACE.fill((0, 0, 0))
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
