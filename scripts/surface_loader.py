from nostalgiaeraycasting import RayCaster


from scripts.utils import load_image, repeat_texture


def load_static_surfaces(caster: RayCaster) -> None:
    wall_texture = load_image("data", "images", "textures", "wall_texture.png")

    # {"image", "A_x", "A_y", "A_z", "B_x", "B_y", "B_z","C_x", "C_y", "C_z", "rm", NULL};
    caster.add_surface(
        repeat_texture(wall_texture, 5, 3),
        -2, 3, 4,
        3, 0, 4,
    )
    caster.add_surface(
        repeat_texture(wall_texture, 7, 3),
        -2, 3, -3,
        -2, 0, 4,
    )
    caster.add_surface(
        repeat_texture(wall_texture, 7, 3),
        3, 3, 4,
        3, 0, -3,
    )
    caster.add_surface(
        repeat_texture(wall_texture, 5, 3),
        3, 3, -3,
        -2, 0, -3,
    )

    caster.add_surface(
        repeat_texture(load_image("data", "images", "textures", "ground_texture.png"), 5, 7),
        3.05, 0, -3.05,
        -2.05, 0, 4.05,
        3.05, 0, 4.05,
    )
    caster.add_surface(
        repeat_texture(load_image("data", "images", "textures", "ceiling_texture.png"), 5, 7),
        3.05, 3, 4.05,
        -2.05, 3.01, -3.05,
        3.05, 3.01, -3.05,
    )