from typing import Generator
from math import sin, cos, radians
from enum import Enum, auto

from os.path import join as join_path
from os import listdir

from pygame import Surface
from pygame.image import load as pg_image_load

from nostalgiaeraycasting import RayCaster


class GameState(Enum):
    SPLASH_SCREEN = auto()
    MAIN_MENU = auto()
    QUIT = auto()
    PLAYING = auto()
    GAME_OVER = auto()


def load_image(*path: str) -> Surface:
    """Load an image from a path.
    @param path: The path to the image.
    :return: The loaded image.
    """
    return pg_image_load(join_path(*path)).convert_alpha()


def lazy_load_images(*path: str) -> Generator:
    """Load images from a directory """
    path: str = join_path(*path)
    for file_path in listdir(path):
        yield load_image(path, file_path)


def repeat_texture(texture: Surface, repeat_x: int = 1, repeat_y: int = 1) -> Surface:
    """Repeat a texture.
    @param texture: The texture to repeat.
    @param repeat_x: The amount of times to repeat the texture horizontally.
    @param repeat_y: The amount of times to repeat the texture vertically.
    :return: The repeated texture.
    """
    width, height = texture.get_size()
    new_surface = Surface((width * repeat_x, height * repeat_y))
    for x in range(repeat_x):
        for y in range(repeat_y):
            new_surface.blit(texture, (x * width, y * height))
    return new_surface.convert_alpha()


def distance(a: tuple[float, float, float], b: tuple[float, float, float]):
    return ((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2 + (a[2] - b[2]) ** 2) ** 0.5


def line_point_distance(point: tuple[float, float, float],
                        line_point: tuple[float, float, float],
                        direction: tuple[float, float, float]):
    looking_at = (direction[0] + line_point[0], direction[1] + line_point[1], direction[2] + line_point[2])
    w = (point[0] - line_point[0], point[1] - line_point[1], point[2] - line_point[2])
    ps = w[0] * direction[0] + w[1] * direction[1] + w[2] * direction[2]

    if ps <= 0:  # point is behind line_point
        return float('inf')   # (w[0] ** 2 + w[1] ** 2 + w[2] ** 2) ** 0.5

    l2 = direction[0] ** 2 + direction[1] ** 2 + direction[2] ** 2
    # if ps >= l2:  # point is beyond line_point
    #     return ((point[0] - looking_at[0]) ** 2 + (point[1] - looking_at[1]) ** 2 + (point[2] - looking_at[2]) ** 2) ** 0.5

    tmp = ps / l2

    return ((point[0] - (line_point[0] + direction[0] * tmp)) ** 2
            + (point[1] - (line_point[1] + direction[1] * tmp)) ** 2
            + (point[2] - (line_point[2] + direction[2] * tmp)) ** 2) ** 0.5


def stereo_distance(line_start: tuple[float, float, float], line_end: tuple[float, float, float], point: tuple[float, float, float]) -> float:
    return (line_end[0] - line_start[0]) * (point[2] - line_start[2]) - (line_end[2] - line_start[2]) * (point[0] - line_start[0])


def set_stereo_volume(player, sound_pos, channel, hear_distance: float = 7., hear_stereo_distance: float = 3.):
    volume: float = max(0., 1. - distance(player.pos, sound_pos) / hear_distance)
    stereo_dist = max(-1., min(1., stereo_distance(
        player.pos,
        (player.pos[0] + player.look_direction[0], player.pos[1] + player.look_direction[1], player.pos[2] + player.look_direction[2]),
        sound_pos
    ) / hear_stereo_distance))

    channel.set_volume(volume * ((stereo_dist + 1) / 2), volume * ((-stereo_dist + 1) / 2))


def add_surface_toward_player_2d(caster: RayCaster, player, image: Surface, pos: tuple[float, float, float], width, height):
    # {"image", "A_x", "A_y", "A_z", "B_x", "B_y", "B_z","C_x", "C_y", "C_z", "rm", NULL};
    caster.add_surface(
        image,
        pos[0] + (width / 2) * cos(radians(player.angle_y + 90)),
        pos[1] + height,
        pos[2] + (width / 2) * sin(radians(player.angle_y + 90)),

        pos[0] - (width / 2) * cos(radians(player.angle_y + 90)),
        pos[1],
        pos[2] - (width / 2) * sin(radians(player.angle_y + 90)),
        rm=True
    )
