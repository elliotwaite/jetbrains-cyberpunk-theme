import json
import os

CUR_DIR = os.path.dirname(os.path.realpath(__file__))
THEME_JSON_PATH = os.path.join(
    CUR_DIR, '..', '..', 'resources/cyberpunk_theme.theme.json'
)
ICLS_PATH = os.path.join(CUR_DIR, 'Cyberpunk_Theme.icls')
OUTPUT_PATH = os.path.join(CUR_DIR, '..', '..', 'resources/cyberpunk_theme.xml')


def main():
    # Get the theme colors (a dict that maps color names to hex strings).
    with open(THEME_JSON_PATH) as f:
        theme_colors = json.load(f)['colors']

    # Get the theme that has color names as values.
    with open(ICLS_PATH) as f:
        color_scheme = f.read()

    # Replace the color names with their corresponding hex values.
    for color_name, hex_str in theme_colors.items():
        color_scheme = color_scheme.replace(
            f'value="{color_name}"',
            f'value="{hex(int(hex_str[1:], 16))[2:]}"',
        )

    # Write the updated theme to the output path.
    with open(OUTPUT_PATH, 'w') as f:
        f.write(color_scheme)


if __name__ == '__main__':
    main()
