from typing import Sequence

from pygame import key as pg_key
from pygame import K_RETURN, K_ESCAPE, K_SPACE


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
        if cls._skip:
            return False

        if any(cls.keys[k] for k in (K_RETURN, K_ESCAPE, K_SPACE)):
            cls._skip = True
            return True

        cls._skip = False
        return False




