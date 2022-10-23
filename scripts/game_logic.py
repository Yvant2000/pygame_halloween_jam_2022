from pygame import Surface

from scripts.player_controler import Player
from scripts.display import DISPLAY
from scripts.text import TEXT
from scripts.input_handler import INPUT
from scripts.game_over import GAME_OVER_SCREEN
from scripts.surface_loader import load_static_surfaces
from scripts.interactions import Interaction, Test_Interaction
from scripts.monsters import Monster, Hangman
from scripts.visuals import hand_visual, VISUALS
from scripts.utils import GameState


from nostalgiaeraycasting import RayCaster


class GAME_LOGIC:
    HOUR_DURATION: float = 120.

    PLAYER: Player
    RAY_CASTER: RayCaster
    SURFACE: Surface

    hour: int
    remaining_time: float
    time_stopped: bool

    interaction_list: list[Interaction]
    monster_list: dict[str, Monster]

    ENDLESS: bool

    @classmethod
    def reset(cls, endless: bool = False):
        cls.ENDLESS = endless

        VISUALS.reset()

        cls.PLAYER = Player()
        cls.RAY_CASTER = RayCaster()
        cls.SURFACE = Surface((128, 72))  # 16:9

        load_static_surfaces(cls.RAY_CASTER)

        cls.hour = 0
        cls.remaining_time = cls.HOUR_DURATION
        cls.time_stopped = False

        cls.interaction_list = [
            Test_Interaction((0, 0, 0)),
        ]

        cls.monster_list = {
            "Hangman": Hangman(),
        }
        # cls.monster_list["Hangman"].aggressiveness = 20

        TEXT.replace("Inspect the room.")

    @classmethod
    def update(cls) -> None:

        cls.PLAYER.update()
        cls.display()

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
    def display(cls) -> None:

        for monster in cls.monster_list.values():
            monster.draw()

        cls.SURFACE.fill((0, 0, 0))

        # {"x", "y", "z", "intensity", "red", "green", "blue", "direction_x", "direction_y", "direction_z", NULL};
        cls.RAY_CASTER.add_light(
            cls.PLAYER.x, cls.PLAYER.height, cls.PLAYER.z,
            3.,
            0.15, 0.07, 0.05,
        )
        if cls.PLAYER.use_flashlight:
            cls.RAY_CASTER.add_light(
                cls.PLAYER.x, cls.PLAYER.y + cls.PLAYER.height, cls.PLAYER.z,
                DISPLAY.VIEW_DISTANCE, 0.5, 0.6, 0.7,
                direction_x=cls.PLAYER.x + cls.PLAYER.look_direction[0] * DISPLAY.VIEW_DISTANCE * 1.8,
                direction_y=cls.PLAYER.y + cls.PLAYER.height + cls.PLAYER.look_direction[1] * DISPLAY.VIEW_DISTANCE * 1.8,
                direction_z=cls.PLAYER.z + cls.PLAYER.look_direction[2] * DISPLAY.VIEW_DISTANCE * 1.8,
            )

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
