from random import randint, choice as random_choice


from pygame import Surface
from pygame.transform import scale, flip
from pygame.mixer import music as pg_music, Sound

from scripts.player_controler import Player
from scripts.display import DISPLAY
from scripts.text import TEXT
from scripts.input_handler import INPUT
from scripts.game_over import GAME_OVER_SCREEN
from scripts.surface_loader import load_static_surfaces
from scripts.visuals import hand_visual, VISUALS, wardrobe_visual, watcher_hand_visual, madness_visual
from scripts.utils import GameState, join_path


from nostalgiaeraycasting import RayCaster
from nostalgiaefilters import distortion

why_are_you_leaving_sound: Sound = Sound(join_path("data", "sounds", "whisper", "why_are_you_leaving.ogg"))


class GAME_LOGIC:
    HOUR_DURATION: float

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
    phone_alert: bool

    watcher_caught: bool
    watcher_hands: float

    score: int

    win: bool

    @classmethod
    def reset(cls, endless: bool = False, graphics: int = 1):
        from scripts.monsters import Hangman, Mimic, Crawler, Guest, Mom, Dad, Watcher, Eye, Hallucination
        from scripts.interactions import BedsideLamp, Bed, FlashLight, Wardrobe, BabyPhone, MimicGift, Door, PissDrawer, Window

        cls.ENDLESS = endless

        VISUALS.reset()
        VISUALS.vignette = 5.

        cls.HOUR_DURATION = 60.
        cls.remaining_time = 20.
        cls.hour = 0

        cls.PLAYER = Player()
        cls.RAY_CASTER = RayCaster()
        cls.SURFACE = Surface((128*graphics, 72*graphics))  # 16:9

        load_static_surfaces(cls.RAY_CASTER)

        cls.time_stopped = False

        cls.door_open = False
        cls.wardrobe_open = False
        cls.phone_alert: bool = True

        cls.watcher_caught = False
        cls.watcher_hands = -3.0

        cls.win = False

        cls.score = 0

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

        if cls.ENDLESS:
            GAME_OVER_SCREEN.get_leaderboard()
            for i in range(8):
                list(cls.monster_list.values())[i].aggressiveness = 5

        # cls.monster_list["Hangman"].aggressiveness = 20
        # cls.monster_list["Mimic"].aggressiveness = 20
        # cls.monster_list["Crawler"].aggressiveness = 20
        # cls.monster_list["Mom"].aggressiveness = 20
        # cls.monster_list["Dad"].aggressiveness = 20
        # cls.monster_list["Eye"].aggressiveness = 20
        # cls.monster_list['Guest'].aggressiveness = 20
        # cls.monster_list["Watcher"].aggressiveness = 20

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
            PissDrawer((-1.6, 0.1, 2.6)),
            MimicGift((-2.3, 0.4, -0.2)),
            door,
            window,
        ]

        if not cls.ENDLESS:
            cls.interaction_list.append(BabyPhone((-1.5, 1.1, 2.7)))

        TEXT.replace("Inspect the room with the MOUSE.", duration=3, fade_out=0, force=True)
        TEXT.add("Move with WASD.", duration=3, fade_out=0, force=True)
        TEXT.add("Interact with LEFT CLICK.", force=True)

    @classmethod
    def update(cls) -> None:
        if cls.PLAYER.x > 2.12:
            if cls.door_open:
                VISUALS.vignette = VISUALS.min_vignette + 3 * (cls.PLAYER.x - 2.08) / .49
                VISUALS.distortion = VISUALS.min_distortion + 5 * (cls.PLAYER.x - 2.08) / .49
                VISUALS.shake = (cls.PLAYER.x - 2.08) / .49
                if cls.PLAYER.x > 2.3:
                    if why_are_you_leaving_sound.get_num_channels() < 1:
                        why_are_you_leaving_sound.play()
                    if len(TEXT.text_list) < 2:
                        TEXT.add(
                            f"{' ' * randint(0, 6) + 'WHY ARE YOU LEAVING ?': ^36}",
                            duration=0.09, fade_out=0., color=(45, 5, 5), font="HelpMe",
                            y=randint(50, DISPLAY.screen_size[1] - 50), size=int(32)
                        )
            else:
                cls.PLAYER.x = 2.08

        if not pg_music.get_busy() and cls.hour > 1:
            if not randint(0, int(120 / DISPLAY.delta_time)):
                pg_music.load(join_path("data", "sounds", "music", random_choice((
                    "stretched_ambiance",
                    "tasto_cello",
                    "harmonic",
                    "chatter",
                    "choir",
                )) + ".ogg"))
                pg_music.play()

        cls.PLAYER.update()
        cls.display()

        cls.score += DISPLAY.delta_time * 100

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
            if cls.ENDLESS or cls.hour > 0 or not cls.phone_alert:
                cls.remaining_time -= DISPLAY.delta_time

            if cls.remaining_time <= 0:
                cls.hour += 1
                VISUALS.min_vignette += 0.05
                VISUALS.vignette += 0.05
                VISUALS.min_distortion += 0.05
                VISUALS.distortion += 0.05
                VISUALS.madness += 0.005
                if not cls.ENDLESS:
                    cls.HOUR_DURATION += 10
                    if cls.hour < 10:
                        cls.phone_alert = True
                    match cls.hour:
                        case 1:
                            cls.monster_list["Eye"].aggressiveness = 18
                        case 2:
                            cls.monster_list["Eye"].aggressiveness = 6
                            cls.monster_list["Guest"].aggressiveness = 13
                        case 3:
                            cls.monster_list["Guest"].aggressiveness = 1
                            cls.monster_list["Eye"].aggressiveness = 7
                            cls.monster_list["Watcher"].aggressiveness = 15
                        case 4:
                            cls.monster_list["Watcher"].aggressiveness = 3
                            cls.monster_list["Guest"].aggressiveness = 2
                            cls.monster_list["Eye"].aggressiveness = 8
                            cls.monster_list["Mimic"].aggressiveness = 10
                        case 5:
                            cls.monster_list["Mimic"].aggressiveness = 2
                            cls.monster_list["Watcher"].aggressiveness = 5
                            cls.monster_list["Eye"].aggressiveness = 9
                            cls.monster_list["Crawler"].aggressiveness = 15
                        case 6:
                            cls.monster_list["Crawler"].aggressiveness = 5
                            cls.monster_list["Mimic"].aggressiveness = 3
                            cls.monster_list["Watcher"].aggressiveness = 6
                            cls.monster_list["Guest"].aggressiveness = 3
                            cls.monster_list["Eye"].aggressiveness = 10
                            cls.monster_list["Hangman"].aggressiveness = 12
                        case 7:
                            cls.monster_list["Hangman"].aggressiveness = 4
                            cls.monster_list["Mimic"].aggressiveness = 4
                            cls.monster_list["Watcher"].aggressiveness = 7
                            cls.monster_list["Mom"].aggressiveness = 13
                        case 8:
                            cls.monster_list["Mom"].aggressiveness = 5
                            cls.monster_list["Hangman"].aggressiveness = 6
                            cls.monster_list["Mimic"].aggressiveness = 5
                            cls.monster_list["Watcher"].aggressiveness = 8
                            cls.monster_list["Guest"].aggressiveness = 7
                            cls.monster_list["Dad"].aggressiveness = 12
                        case 9:
                            cls.monster_list["Dad"].aggressiveness = 7
                            cls.monster_list["Mom"].aggressiveness = 8
                            cls.monster_list["Hangman"].aggressiveness = 8
                            cls.monster_list["Crawler"].aggressiveness = 8
                            cls.monster_list["Mimic"].aggressiveness = 7
                            cls.monster_list["Guest"].aggressiveness = 5
                            cls.monster_list["Hallucination"].aggressiveness = 5
                            pg_music.load(join_path("data", "sounds", "music", "music_box.ogg"))
                            pg_music.play(fade_ms=8000)

                        case 10:
                            for monster in cls.monster_list.values():
                                monster.state = 0
                                monster.aggressiveness = 0
                            cls.win = True
                            pg_music.stop()
                            pg_music.load(join_path("data", "sounds", "sfx", "birds.ogg"))
                            pg_music.play(fade_ms=10000)
                            cls.HOUR_DURATION = 10.
                        case 11:
                            GAME_OVER_SCREEN.killer = ""
                            GAME_OVER_SCREEN.reason = "You survived the night!"
                            cls.game_over()
                else:
                    for _ in range(3):
                        list(cls.monster_list.values())[randint(0, 7)].aggressiveness += 1
                cls.remaining_time = cls.HOUR_DURATION

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

        if cls.win:
            if VISUALS.min_distortion > 0:
                VISUALS.min_distortion -= 0.1 * DISPLAY.delta_time
            if VISUALS.min_vignette > 0:
                VISUALS.min_vignette -= 0.1 * DISPLAY.delta_time
            cls.RAY_CASTER.add_light(
                3.0, 1.0, 2.0,
                15 * (10 - cls.remaining_time) / 10,
                1.0, 1.0, 1.0,
            )

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
                -0.4, cls.PLAYER.height, -3.4 - max(0., cls.watcher_hands * 0.19),
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
                    return
                cls.watcher_hands += DISPLAY.delta_time * 2.3
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
        GAME_OVER_SCREEN.reset(cls.ENDLESS, cls.score)
