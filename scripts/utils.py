from typing import Generator
from enum import Enum, auto

from os.path import join as join_path
from os import listdir

from pygame import Surface
from pygame.image import load as pg_image_load


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

    if ps <= 0:
        return (w[0] ** 2 + w[1] ** 2 + w[2] ** 2) ** 0.5

    l2 = direction[0] ** 2 + direction[1] ** 2 + direction[2] ** 2
    if ps >= l2:
        return ((point[0] - looking_at[0]) ** 2 + (point[1] - looking_at[1]) ** 2 + (point[2] - looking_at[2]) ** 2) ** 0.5

    tmp = ps / l2

    return ((point[0] - (line_point[0] + direction[0] * tmp)) ** 2
            + (point[1] - (line_point[1] + direction[1] * tmp)) ** 2
            + (point[2] - (line_point[2] + direction[2] * tmp)) ** 2) ** 0.5
