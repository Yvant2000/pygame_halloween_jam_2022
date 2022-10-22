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
