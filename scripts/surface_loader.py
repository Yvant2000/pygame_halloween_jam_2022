from nostalgiaeraycasting import RayCaster


from scripts.utils import load_image, repeat_texture


def load_static_surfaces(caster: RayCaster) -> None:
    wall_texture = load_image("data", "images", "textures", "wall_texture.png")

    # WALLS

    # {"image", "A_x", "A_y", "A_z", "B_x", "B_y", "B_z","C_x", "C_y", "C_z", "rm", NULL};
    caster.add_surface(
        repeat_texture(wall_texture, 5, 3),
        -2.5, 3, 3.5,
        2.5, 0, 3.5,
    )
    caster.add_surface(
        repeat_texture(wall_texture, 7, 3),
        -2.5, 3, -3.5,
        -2.5, 0, 3.5,
    )
    caster.add_surface(
        repeat_texture(wall_texture, 7, 3),
        2.5, 3, 3.5,
        2.5, 0, -3.5,
    )
    caster.add_surface(
        repeat_texture(wall_texture, 5, 3),
        2.5, 3, -3.5,
        -2.5, 0, -3.5,
    )

    del wall_texture

    # FLOOR
    caster.add_surface(
        repeat_texture(load_image("data", "images", "textures", "ground_texture.png"), 5, 7),
        2.55, 0, -3.55,
        -2.55, 0, 3.55,
        2.55, 0, 3.55,
    )
    # CEILING
    caster.add_surface(
        repeat_texture(load_image("data", "images", "textures", "ceiling_texture.png"), 5, 7),
        2.55, 3, 3.55,
        -2.55, 3.01, -3.55,
        2.55, 3.01, -3.55,
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
        -0.8, 0.4, 3.5,
        -0.8, 0, 1.5)
    caster.add_surface(
        load_image("data", "images", "props", "bed_right.png"),
        0.8, 0, 3.5,
        0.8, 0.4, 1.5)

    caster.add_surface(
        load_image("data", "images", "props", "front_bed.png"),
        -0.8, 0.4, 1.52,
        0.8, 0.0, 1.52)

    # WARDROBE
    caster.add_surface(
        load_image("data", "images", "props", "wardrobe_right_door.png"),
        -0.8, 2.0, -3.2,
        -1.6, 0.0, -3.2)

    caster.add_surface(
        load_image("data", "images", "props", "wardrobe_side.png"),
        0.0, 2.0, -3.2,
        0.0, 0.0, -3.5)

    caster.add_surface(
        load_image("data", "images", "props", "wardrobe_side.png"),
        -1.6, 2.0, -3.2,
        -1.6, 0.0, -3.5)

    caster.add_surface(
        load_image("data", "images", "props", "wardrobe_top.png"),
        -1.6, 1.9, -3.5,
        0.0, 1.91, -3.2,
        -1.6, 1.91, -3.2)

    #NIGHTSTAND

    caster.add_surface(
        load_image("data", "images", "props", "nightstand_front.png"),
        0.9, 0.5, 3.01,
        1.5, 0.0, 3.01)

    caster.add_surface(
        load_image("data", "images", "props", "nightstand_side.png"),
        0.9, 0.5, 3.0,
        0.9, 0.0, 3.5)

    caster.add_surface(
        load_image("data", "images", "props", "nightstand_side.png"),
        1.5, 0.5, 3.0,
        1.5, 0.0, 3.5)

    caster.add_surface(
        load_image("data", "images", "props", "nightstand_top.png"),
        0.9, 0.5, 3.5,
        1.5, 0.5, 3.0,
        0.9, 0.5, 3.0)

