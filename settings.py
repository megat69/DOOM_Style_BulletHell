"""
Contains the SETTINGS class, allowing every other file to access the game's settings.
"""
import json
import math

# Loading the settings
with open("settings.json", "r", encoding="utf-8") as settings_file:
    class SETTINGS:
        SETTINGS_AS_JSON = json.load(settings_file)

    def add_attrs_to_settings(cls, dictionary):
        for key, value in dictionary.items():
            if isinstance(value, dict):
                setattr(cls, key, SETTINGS())
                add_attrs_to_settings(getattr(cls, key), value)
            else:
                setattr(cls, key, value)
    add_attrs_to_settings(SETTINGS, SETTINGS.SETTINGS_AS_JSON)
    del add_attrs_to_settings

    # Dynamic settings
    SETTINGS.graphics.fov = math.pi / 2.5
    SETTINGS.graphics.half_fov = SETTINGS.graphics.fov / 2
    SETTINGS.graphics.num_rays = SETTINGS.graphics.resolution[0] // 2
    SETTINGS.graphics.half_num_rays = SETTINGS.graphics.num_rays / 2
    SETTINGS.graphics.delta_angle = SETTINGS.graphics.fov / SETTINGS.graphics.num_rays
    SETTINGS.graphics.half_width = SETTINGS.graphics.resolution[0] // 2
    SETTINGS.graphics.half_height = SETTINGS.graphics.resolution[1] // 2
    SETTINGS.graphics.screen_distance = SETTINGS.graphics.half_width / math.tan(SETTINGS.graphics.half_fov)
    SETTINGS.graphics.scale = SETTINGS.graphics.resolution[0] // SETTINGS.graphics.num_rays
    SETTINGS.graphics.half_texture_size = SETTINGS.graphics.texture_size // 2
    SETTINGS.controls.mouse_border_right = SETTINGS.graphics.resolution[0] - SETTINGS.controls.mouse_border_left
