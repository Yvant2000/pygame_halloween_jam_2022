from math import sin


from pygame import Surface


from scripts.display import DISPLAY
from scripts.utils import load_image


from nostalgiaefilters import vignette, fish, distortion


hand_visual: Surface = load_image("data", "images", "visuals", "hand.png")
wardrobe_visual: Surface = load_image("data", "images", "visuals", "wardrobe.png")
watcher_hand_visual: Surface = load_image("data", "images", "visuals", "watcher_hand.png")
madness_visual: Surface = load_image("data", "images", "visuals", "madness.png")


class VISUALS:
    vignette: float
    min_vignette: float

    shake: float
    min_shake: float
    _shake: float

    fish_eye: float
    min_fish_eye: float

    distortion: float
    min_distortion: float

    fried: float
    min_fried: float

    madness: float

    @classmethod
    def reset(cls):
        cls.vignette = 0.
        cls.min_vignette = 0.

        cls.shake = 0.
        cls.min_shake = 0.
        cls._shake = 0.

        cls.fish_eye = 0.
        cls.min_fish_eye = 0.

        cls.distortion = 0.
        cls.min_distortion = 0.

        cls.fried = 0.
        cls.min_fried = 0.

        cls.madness = 0.

    @classmethod
    def display(cls):
        if cls.shake:
            cls._shake += DISPLAY.delta_time
            effect = DISPLAY.screen.copy()
            DISPLAY.screen.fill((0, 0, 0))
            DISPLAY.screen.blit(
                effect,
                (((sin(cls._shake) * 1000) % cls.shake - cls.shake/2) * 20,
                 ((sin(cls._shake) * 10000) % cls.shake - cls.shake/2) * 15))
            cls.shake = max(cls.min_shake, cls.shake - DISPLAY.delta_time)

        if cls.fish_eye:
            effect = DISPLAY.screen.copy()
            fish(effect, DISPLAY.screen, 0 - cls.fish_eye)
            cls.fish_eye = max(cls.min_fish_eye, cls.fish_eye - DISPLAY.delta_time)

        if cls.fried:
            effect = DISPLAY.screen.copy()
            distortion(effect, DISPLAY.screen, True, True, cls.fried * 20, 100, 1)
            cls.fried = max(cls.min_fried, cls.fried - DISPLAY.delta_time)

        if cls.distortion:
            effect = Surface(DISPLAY.screen_size)
            distortion(DISPLAY.screen, effect, True, True, 10, 0.01 * cls.distortion, 0.1 * cls.distortion)
            effect.set_alpha(int(cls.distortion * 100))
            DISPLAY.screen.blit(effect, (0, 0))
            cls.distortion = max(cls.min_distortion, cls.distortion - DISPLAY.delta_time)

        if cls.vignette:
            vignette(DISPLAY.screen, strength=cls.vignette * 5)
            cls.vignette = max(cls.min_vignette, cls.vignette - DISPLAY.delta_time)
