from pygame import Surface
from pygame.transform import scale, flip

from scripts.player_controler import Player
from scripts.display import DISPLAY
from scripts.text import TEXT
from scripts.input_handler import INPUT
from scripts.game_over import GAME_OVER_SCREEN
from scripts.surface_loader import load_static_surfaces
from scripts.visuals import hand_visual, VISUALS, wardrobe_visual, watcher_hand_visual, madness_visual
from scripts.utils import GameState


from nostalgiaeraycasting import RayCaster
from nostalgiaefilters import distortion


class GAME_LOGIC:
    HOUR_DURATION: float = 140.

    PLAYER: Player
    RAY_CASTER: RayCaster
    SURFACE: Surface

    hour: int
    remaining_time: float
    time_stopped: bool

    interaction_list: list
    monster_list: dict

    ENDLESS: bool

    door_open: bool
    wardrobe_open: bool

    watcher_caught: bool
    watcher_hands: float

    @classmethod
    def reset(cls, endless: bool = False):
        from scripts.monsters import Hangman, Mimic, Crawler, Guest, Mom, Dad, Watcher, Eye, Hallucination
        from scripts.interactions import BedsideLamp, Bed, FlashLight, Wardrobe, BabyPhone, MimicGift, Door, PissDrawer, Window

        cls.ENDLESS = endless

        VISUALS.reset()
        VISUALS.vignette = 5.

        cls.PLAYER = Player()
        cls.RAY_CASTER = RayCaster()
        cls.SURFACE = Surface((128*3, 72*3))  # 16:9

        load_static_surfaces(cls.RAY_CASTER)

        cls.hour = 0
        cls.remaining_time = cls.HOUR_DURATION
        cls.time_stopped = False

        cls.door_open = False
        cls.wardrobe_open = False

        cls.watcher_caught = False
        cls.watcher_hands = -3.0

        cls.monster_list = {
            "Hangman": Hangman(),
            "Mimic": Mimic(),
            "Crawler": Crawler(),
            "Guest": Guest(),
            "Mom": Mom(),
            "Dad": Dad(),
            "Watcher": Watcher(),
            "Eye": Eye(),
            "Hallucination": Hallucination(),
        }
        # cls.monster_list["Hangman"].aggressiveness = 20
        # cls.monster_list["Mimic"].aggressiveness = 20
        # cls.monster_list["Crawler"].aggressiveness = 20
        # cls.monster_list["Mom"].aggressiveness = 20
        # cls.monster_list["Dad"].aggressiveness = 20

        door = Door((2.499, 1.0, -0.6))
        cls.monster_list['Mom'].door = door
        cls.monster_list['Dad'].door = door
        window = Window((2.49, 1.0, 2.0))
        cls.monster_list['Eye'].window = window

        cls.interaction_list = [
            FlashLight((1.8, 0.4, -3.2)),
            BedsideLamp((1.3, 0.5, 3.2)),
            Bed((0, 0.5, 3)),
            Wardrobe((0, 1, -3.21), (-0.4, 1, -3.5)),
            BabyPhone((-1.5, 1.1, 2.7)),
            MimicGift((-2.3, 0.4, -0.2)),
            door,
            PissDrawer((-1.6, 0.1, 2.6)),
            window,
        ]

        TEXT.replace("Inspect the room with the MOUSE.", duration=3, fade_out=0, force=True)
        TEXT.add("Move with WASD.", duration=3, fade_out=0, force=True)
        TEXT.add("Interact with LEFT CLICK.", force=True)

        VISUALS.madness = 0

    @classmethod
    def update(cls) -> None:

        cls.PLAYER.update()
        cls.display()

        if not (cls.PLAYER.in_bed or cls.PLAYER.in_wardrobe):
            for interaction in cls.interaction_list:
                if interaction.can_interact(cls.PLAYER):
                    DISPLAY.screen.blit(
                        hand_visual, (DISPLAY.screen_size[0] // 2 - hand_visual.get_width() // 2,
                                      DISPLAY.screen_size[1] // 2 - hand_visual.get_height() // 2)
                    )
                    if INPUT.interact():
                        interaction.interact(cls.PLAYER)
                    break

        for interaction in cls.interaction_list:
            interaction.update(cls.PLAYER)

        for monster in cls.monster_list.values():
            monster.update()

        if not cls.time_stopped:
            cls.remaining_time -= DISPLAY.delta_time
            if cls.remaining_time <= 0:
                cls.hour += 1
                cls.remaining_time = cls.HOUR_DURATION

    @classmethod
    def hour_event(cls) -> None:
        """
        Called every hour.
        Define the new events happening at each hour.
        """
        match cls.hour:
            case 1:
                ...
            case _:
                ...

    @classmethod
    def display(cls) -> None:

        for monster in cls.monster_list.values():
            monster.draw()

        cls.SURFACE.fill((0, 0, 0))
        if VISUALS.madness:
            madness_visual.set_alpha(int(VISUALS.madness * 100))
            effect = Surface((cls.SURFACE.get_size()))
            effect.blit(scale(madness_visual, cls.SURFACE.get_size()), (0, 0))
            distortion(effect, cls.SURFACE, True, True, cls.SURFACE.get_width() * 0.03, 0.01 + VISUALS.madness * 0.05, 0.03)

        # {"z", "y", "z", "intensity", "red", "green", "blue", "direction_x", "direction_y", "direction_z", NULL};
        cls.RAY_CASTER.add_light(
            cls.PLAYER.x, cls.PLAYER.height, cls.PLAYER.z,
            3.,
            0.07, 0.07, 0.20,
        )

        if cls.PLAYER.in_bed:
            if cls.PLAYER.use_flashlight:
                cls.RAY_CASTER.add_light(
                    0, 0.5, 3.0,
                    DISPLAY.VIEW_DISTANCE,
                    0.5, 0.6, 0.7,
                    direction_x=0,
                    direction_y=1,
                    direction_z=-3,
                )

            cls.RAY_CASTER.raycasting(
                cls.SURFACE,
                0, 0.5, 3.2,
                10,
                -90,
                DISPLAY.FOV,
                DISPLAY.VIEW_DISTANCE,
            )
        elif cls.PLAYER.in_wardrobe or cls.watcher_caught:
            if cls.PLAYER.use_flashlight:
                cls.RAY_CASTER.add_light(
                    -0.4, cls.PLAYER.height, -3.3,
                    DISPLAY.VIEW_DISTANCE,
                    0.5, 0.6, 0.7,
                    direction_x=-0.4,
                    direction_y=cls.PLAYER.height,
                    direction_z=5.0,
                )

            cls.RAY_CASTER.raycasting(
                cls.SURFACE,
                -0.4, cls.PLAYER.height, -3.4 - max(0., cls.watcher_hands * 0.3),
                0,
                90,
                DISPLAY.FOV,
                DISPLAY.VIEW_DISTANCE,
            )

            cls.SURFACE.blit(scale(wardrobe_visual, cls.SURFACE.get_size()), (0, 0))
            if cls.watcher_caught:
                cls.PLAYER.in_wardrobe = True

                h = cls.SURFACE.get_height()
                nw = watcher_hand_visual.get_width() * h / watcher_hand_visual.get_height()
                surf = scale(watcher_hand_visual, (nw, h))

                w = cls.SURFACE.get_width()
                cls.SURFACE.blit(surf, (cls.watcher_hands * 0.7 * w - nw, 0))
                cls.SURFACE.blit(flip(surf, True, False), (w - cls.watcher_hands * 0.7 * w, 0))
                if cls.watcher_hands >= 1.0:
                    cls.game_over()
                cls.watcher_hands += DISPLAY.delta_time * 3.0
        else:
            if cls.PLAYER.use_flashlight:
                cls.RAY_CASTER.add_light(
                    cls.PLAYER.x, cls.PLAYER.y + cls.PLAYER.height, cls.PLAYER.z,
                    DISPLAY.VIEW_DISTANCE, 0.5, 0.6, 0.7,
                    direction_x=cls.PLAYER.x + cls.PLAYER.look_direction[0] * DISPLAY.VIEW_DISTANCE * 1.8,
                    direction_y=cls.PLAYER.y + cls.PLAYER.height + cls.PLAYER.look_direction[
                        1] * DISPLAY.VIEW_DISTANCE * 1.8,
                    direction_z=cls.PLAYER.z + cls.PLAYER.look_direction[2] * DISPLAY.VIEW_DISTANCE * 1.8,
                )

            # {"dst_surface", "z", "y", "z", "angle_x", "angle_y", "fov", "view_distance", "rad", NULL};
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
        cls.RAY_CASTER.clear_lights()

        DISPLAY.display_scaled(cls.SURFACE)

        # DISPLAY VISUALS

        VISUALS.display()

        TEXT.update()

    @classmethod
    def game_over(cls):
        from scripts.game import GAME
        GAME.state = GameState.GAME_OVER
        GAME_OVER_SCREEN.reset()
