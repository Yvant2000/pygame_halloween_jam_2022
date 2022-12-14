from nostalgiaeraycasting import RayCaster


from scripts.utils import load_image


def load_static_surfaces(caster: RayCaster) -> None:
    # WALLS

    # {"image", "A_x", "A_y", "A_z", "B_x", "B_y", "B_z","C_x", "C_y", "C_z", "rm", NULL};
    caster.add_surface(
        load_image("data", "images", "textures", "wall_back.png"),
        -2.5, 3, 3.5,
        2.5, 0, 3.5,
    )
    caster.add_surface(
        load_image("data", "images", "textures", "wall_left.png"),
        -2.5, 3, -3.5,
        -2.5, 0, 3.5,
    )
    caster.add_surface(
        load_image("data", "images", "textures", "wall_right.png"),
        2.5, 3, 3.5,
        2.5, 0, -3.5,
    )
    caster.add_surface(
        load_image("data", "images", "textures", "wall_front.png"),
        2.5, 3, -3.5,
        -2.5, 0, -3.5,
    )

    # FLOOR
    caster.add_surface(
        load_image("data", "images", "textures", "ground.png"),
        2.55, 0, -3.55,
        -2.55, 0, 3.55,
        2.55, 0, 3.55,
    )
    # CEILING
    caster.add_surface(
        load_image("data", "images", "textures", "ceiling.png"),
        2.55, 3, 3.55,
        -2.55, 3.01, -3.55,
        2.55, 3.01, -3.55,
    )

    # CORRIDOR

    caster.add_surface(
        load_image("data", "images", "textures", "corridor_wall.png"),
        2.501, 2.3, -0.4,
        10.5, 0., -0.4
    )
    caster.add_surface(
        load_image("data", "images", "textures", "black.png"),
        2.501, 4., -0.3,
        10.5, -2., -0.3
    )

    caster.add_surface(
        load_image("data", "images", "textures", "corridor_wall.png"),
        2.501, 2.3, -1.6,
        10.5, 0., -1.6
    )

    caster.add_surface(
        load_image("data", "images", "textures", "corridor_ground.png"),
        10.5, -0.01, -0.39,
        2.5, -0.01, -1.61,
        2.5, -0.01, -0.39,
    )

    caster.add_surface(
        load_image("data", "images", "textures", "corridor_ceiling.png"),
        10.5, 2.3, -0.39,
        2.51, 2.3, -1.61,
        2.51, 2.3, -0.39,
    )

    # BED
    caster.add_surface(
        load_image("data", "images", "props", "top_bed.png"),
        -0.8, 0.4, 3.5,
        0.8, 0.4, 1.5,
        -0.8, 0.4, 1.5
    )

    caster.add_surface(
        load_image("data", "images", "props", "bed_left.png"),
        -0.79, 0.4, 3.5,
        -0.79, 0, 1.5)
    caster.add_surface(
        load_image("data", "images", "props", "bed_right.png"),
        0.79, 0, 3.5,
        0.79, 0.4, 1.5)

    caster.add_surface(
        load_image("data", "images", "props", "front_bed.png"),
        -0.8, 0.4, 1.51,
        0.8, 0.0, 1.51)

    # WARDROBE

    caster.add_surface(
        load_image("data", "images", "props", "wardrobe_right_door.png"),
        -0.8, 2.0, -3.2,
        -1.6, 0.0, -3.2)

    caster.add_surface(
        load_image("data", "images", "props", "wardrobe_left.png"),
        0.0, 2.0, -3.2,
        0.0, 0.0, -3.5)

    caster.add_surface(
        load_image("data", "images", "props", "wardrobe_right.png"),
        -1.6, 2.0, -3.2,
        -1.6, 0.0, -3.5)

    caster.add_surface(
        load_image("data", "images", "props", "wardrobe_top.png"),
        -0.0, 2.0, -3.2,
        -1.6, 2.01, -3.5,
        -0.0, 2.01, -3.5)

    #NIGHTSTAND

    caster.add_surface(
        load_image("data", "images", "props", "nightstand_front.png"),
        0.9, 0.5, 3.01,
        1.5, 0.0, 3.01)

    caster.add_surface(
        load_image("data", "images", "props", "nightstand_left.png"),
        0.9, 0.5, 3.5,
        0.9, 0.0, 3.0)

    caster.add_surface(
        load_image("data", "images", "props", "nightstand_right.png"),
        1.5, 0.5, 3.0,
        1.5, 0.0, 3.5)

    caster.add_surface(
        load_image("data", "images", "props", "nightstand_top.png"),
        0.9, 0.5, 3.5,
        1.5, 0.5, 3.0,
        0.9, 0.5, 3.0)

    # CLOSET

    caster.add_surface(
        load_image("data", "images", "props", "closet_front.png"),
        -2.0, 1.1, 2.2,
        -1.0, 0.0, 2.5)

    caster.add_surface(
        load_image("data", "images", "props", "closet_left.png"),
        -2.0, 1.1, 2.2,
        -2.3, 0.0, 3.2)

    caster.add_surface(
        load_image("data", "images", "props", "closet_right.png"),
        -1.0, 1.1, 2.5,
        -1.3, 0.0, 3.5)

    caster.add_surface(
        load_image("data", "images", "props", "closet_top.png"),
        -2.3, 1.09, 2.2,
        -1.0, 1.09, 3.5,
        -1.0, 1.09, 2.2,
    )

    # LITTLE TABLE

    caster.add_surface(
        load_image("data", "images", "props", "table_front.png"),
        2.0, 0.4, -3.1,
        0.9, 0.0, -3.1)

    caster.add_surface(
        load_image("data", "images", "props", "table_side.png"),
        0.9, 0.4, -3.1,
        0.9, 0.0, -3.5)

    caster.add_surface(
        load_image("data", "images", "props", "table_top.png"),
        0.9, 0.4, -3.1,
        2.0, 0.4, -3.5,
        0.9, 0.4, -3.5)

    caster.add_surface(
        load_image("data", "images", "props", "photo.png"),
        1.4, 0.65, -3.3,
        1.1, 0.4, -3.2,
        1.4, 0.4, -3.2)
