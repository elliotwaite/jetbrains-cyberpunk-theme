import json
import math

HC_THEME_PATH = 'high_contrast_theme/HighContrast.theme.json'
HC_COLOR_SCHEME_PATH = 'high_contrast_theme/highContrastSchemeWhitened.xml'

THEME_METADATA_PATHS = (
    'theme_metadata/IntelliJPlatform.themeMetadata.json',
    'theme_metadata/JDK.themeMetadata.json',
)

THEME_OUTPUT_PATH = 'debug_theme.theme.json'
COLOR_SCHEME_OUTPUT_PATH = 'debug_theme.xml'

# UI keys with these endings should be ignored because they either don't accept
# color values (such as keys for border widths), or they hide underlying
# content (such as masks).
IGNORED_UI_KEY_ENDINGS = (
    '.underlineHeight',
    '.borderWidth',
    '.borderInsets',
    '.tabSelectionHeight',
    '.backgroundBrightness',
    '.nonFocusedMask',
)

KEYS_WITH_UNFLATTENED_CHILDREN = {'ColorPalette'}


def phi_shuffled(input_iterable):
    PHI = (1 + 5 ** 0.5) / 2
    input_list = list(input_iterable)
    output_list = []
    index_fraction = 0
    while len(input_list):
        index_fraction = (index_fraction + PHI) % 1
        index = math.floor(index_fraction * len(input_list))
        output_list.append(input_list[index])
        input_list = input_list[:index] + input_list[index + 1 :]

    return output_list


def rgb_to_hex_color(rgb):
    r, g, b = rgb
    return f'{r:02x}{g:02x}{b:02x}'


def get_all_saturated_colors():
    colors = (
        [(255, i, 0) for i in range(255)]
        + [(i, 255, 0) for i in range(255, 0, -1)]
        + [(0, 255, i) for i in range(255)]
        + [(0, i, 255) for i in range(255, 0, -1)]
        + [(i, 0, 255) for i in range(255)]
        + [(255, 0, i) for i in range(255, 0, -1)]
    )
    return map(rgb_to_hex_color, colors)


def flattened_dict_keys(source_dict, prefix=''):
    keys = []
    for key, val in source_dict.items():
        if isinstance(val, dict):
            sub_prefix = prefix + key + '.'
            keys.extend(flattened_dict_keys(val, sub_prefix))
        else:
            keys.append(prefix + key)

    return keys


def unflatten_dict(source_dict):
    output_dict = {}
    for key, val in source_dict.items():
        keys = key.split('.')
        target_dict = output_dict
        while len(keys) > 1:
            if keys[0] not in target_dict:
                target_dict[keys[0]] = {}
            target_dict = target_dict[keys[0]]
            if keys[0] in KEYS_WITH_UNFLATTENED_CHILDREN:
                keys = ['.'.join(keys[1:])]
            else:
                keys = keys[1:]
        target_dict[keys[0]] = val

    return output_dict


def get_valid_ui_keys():
    ui_keys = set()

    # Load keys from demo themes.
    with open(HC_THEME_PATH) as f:
        data = json.load(f)
    ui_keys.update(flattened_dict_keys(data['ui'], 'ui.'))
    ui_keys.update(flattened_dict_keys(data['icons'], 'icons.'))

    # Load keys from metadata files.
    for path in THEME_METADATA_PATHS:
        with open(path) as f:
            data = json.load(f)
        for ui_item in data['ui']:
            if 'deprecated' not in ui_item:
                ui_keys.add('ui.' + ui_item['key'])

    ui_keys = [
        ui_key for ui_key in ui_keys if not ui_key.endswith(IGNORED_UI_KEY_ENDINGS)
    ]
    ui_keys.sort()
    return ui_keys


def get_theme_and_updated_color_index(colors, color_index):
    theme = {}
    ui_keys = get_valid_ui_keys()
    for ui_key in ui_keys:
        if ui_key.endswith('.border'):
            # Border values are prefixed by the border widths.
            theme[ui_key] = f'1,1,1,1,{colors[color_index]}'
        else:
            theme[ui_key] = f'#{colors[color_index]}'
        color_index += 1

    theme = unflatten_dict(theme)
    theme = {
        'name': 'Cyberpunk Theme',
        'dark': True,
        'author': 'Elliot Waite',
        'editorScheme': '/cyberpunk.xml',
        'ui': theme['ui'],
        'icons': theme['icons'],
    }

    return theme, color_index


def get_color_scheme(colors, color_index):
    replacement_str = 'ffffff'
    color_scheme = ''
    with open(HC_COLOR_SCHEME_PATH) as f:
        for line in f.readlines():
            if replacement_str in line:
                line = line.replace(replacement_str, colors[color_index])
                color_index += 1
            color_scheme += line

        return color_scheme


def main():
    colors = phi_shuffled(get_all_saturated_colors())
    color_index = 0

    theme, color_index = get_theme_and_updated_color_index(colors, color_index)
    with open(THEME_OUTPUT_PATH, 'w') as f:
        json.dump(theme, f, indent=2)

    color_scheme = get_color_scheme(colors, color_index)
    with open(COLOR_SCHEME_OUTPUT_PATH, 'w') as f:
        f.write(color_scheme)


if __name__ == '__main__':
    main()
