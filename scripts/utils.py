from typing import Generator

from os.path import join as join_path
from os import listdir

from pygame import Surface
from pygame.image import load as pg_image_load


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
