from typing import Sequence

from pygame import key as pg_key
from pygame import K_RETURN, K_SPACE, K_UP, K_DOWN, K_LEFT, K_RIGHT, K_w, K_a, K_d, K_s, K_LSHIFT, K_LCTRL, K_e
from pygame import mouse as pg_mouse

from scripts.display import DISPLAY


class INPUT:

    _skip: bool = False
    _interact: bool = False
    keys: Sequence[bool] = {}
    mouse_pressed: tuple[bool, bool, bool] = (False, False, False)
    rel: tuple[int, int] = (0, 0)

    @classmethod
    def update(cls):
        cls.keys = pg_key.get_pressed()

        if pg_key.get_focused():
            cls.rel = pg_mouse.get_rel()
            pg_mouse.set_visible(False)
            pg_mouse.set_pos((DISPLAY.screen_size[0] // 2, DISPLAY.screen_size[1] // 2))
            cls.mouse_pressed = pg_mouse.get_pressed()
        else:
            cls.rel = (0, 0)
            pg_mouse.set_visible(True)

    @classmethod
    def confirm(cls) -> bool:
        """Tells wether or not the player wants to skip the current screen.
        Waits for the player to stop pressing the skip keys before allowing the player to skip again
        @return: True if the player skipped the splash screen, False otherwise."""

        if any(cls.keys[k] for k in (K_RETURN, K_SPACE)):
            if cls._skip:
                return False

            cls._skip = True
            return True

        cls._skip = False
        return False

    @classmethod
    def up(cls) -> bool:
        return cls.keys[K_UP] or cls.keys[K_w]

    @classmethod
    def down(cls) -> bool:
        return cls.keys[K_DOWN] or cls.keys[K_s]

    @classmethod
    def left(cls) -> bool:
        return cls.keys[K_LEFT] or cls.keys[K_a]

    @classmethod
    def right(cls) -> bool:
        return cls.keys[K_RIGHT] or cls.keys[K_d]

    @classmethod
    def jump(cls) -> bool:
        return cls.keys[K_SPACE]

    @classmethod
    def sprint(cls) -> bool:
        return cls.keys[K_LSHIFT] or cls.keys[K_LCTRL]

    @classmethod
    def interact(cls) -> bool:

        if cls.keys[K_e] or cls.mouse_pressed[0]:
            if cls._interact:
                return False

            cls._interact = True
            return True

        cls._interact = False
        return False
