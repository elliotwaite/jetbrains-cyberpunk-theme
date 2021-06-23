import json
import re

CYBERPUNK_THEME_JSON_PATH = '../../resources/cyberpunk_theme.theme.json'
CYBERPUNK_ICLS_PATH = 'Cyberpunk.icls'
OUTPUT_PATH = '../../resources/cyberpunk_theme.xml'


def main():
    with open(CYBERPUNK_THEME_JSON_PATH) as f:
        theme_colors = json.load(f)['colors']

    with open(CYBERPUNK_ICLS_PATH) as f:
        color_scheme = f.read()

    color_scheme = re.sub(r'  <metaInfo>(.*)</metaInfo>\n', '', color_scheme, flags=re.S)

    for color_name, hex_str in theme_colors.items():
        color_scheme = color_scheme.replace(
            f'value="{color_name}"',
            f'value="{hex(int(hex_str[1:], 16))[2:]}"',
        )

    with open(OUTPUT_PATH, 'w') as f:
        f.write(color_scheme)


if __name__ == '__main__':
  main()
