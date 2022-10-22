from typing import Sequence

from pygame import key as pg_key
from pygame import K_RETURN, K_ESCAPE, K_SPACE, K_UP, K_DOWN, K_LEFT, K_RIGHT, K_w, K_a, K_d, K_s


# noinspection PyClassHasNoInit
class INPUT:

    _skip: bool = False
    keys: Sequence[bool] = {}

    @classmethod
    def update(cls):
        cls.keys = pg_key.get_pressed()

    @classmethod
    def skip(cls) -> bool:
        """Tells wether or not the player wants to skip the current screen.
        Waits for the player to stop pressing the skip keys before allowing the player to skip again
        @return: True if the player skipped the splash screen, False otherwise."""

        if any(cls.keys[k] for k in (K_RETURN, K_ESCAPE, K_SPACE)):
            if cls._skip:
                return False

            cls._skip = True
            return True

        cls._skip = False
        return False

    @classmethod
    def up(cls) -> bool:
        return cls.keys[K_UP] or cls.keys[K_W]

    @classmethod
    def down(cls) -> bool:
        return cls.keys[K_DOWN] or cls.keys[K_S]

    @classmethod
    def left(cls) -> bool:
        return cls.keys[K_LEFT] or cls.keys[K_A]

    @classmethod
    def right(cls) -> bool:
        return cls.keys[K_RIGHT] or cls.keys[K_D]



