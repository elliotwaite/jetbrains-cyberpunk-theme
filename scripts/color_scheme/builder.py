import json
import re

EXPORTED_COLOR_SCHEME_PATH = 'exported_color_scheme.icls'
COLOR_SCHEME_TEMPLATE_PATH = 'color_scheme_template.xml'
THEME_PATH = '../../src/main/resources/cyberpunk.theme.json'

OPTION_PATTERN = re.compile('\s*<option name="([^"]+)" value="([^"]+)" />')
IGNORED_OPTION_NAMES = {
  'FONT_TYPE',
  'EFFECT_TYPE',
  'ScrollBar.Mac.hoverThumbColor',
  'ScrollBar.Mac.thumbColor',
}


def hex_str_to_hex_value(hex_str):
  return hex(int(hex_str[1:], 16))[2:]


def get_theme_color_map(theme_path):
  """Returns a color map for the theme at the specified path.

  Maps from the color name to the lowercase truncated hex value of the color.
  E.g. If the theme has the key value pair 'blue': '#0000FF', the color map
  will have the key value pair 'blue': 'ff'.
  """
  with open(theme_path) as f:
    theme = json.load(f)

  return {name: hex_str_to_hex_value(hex_str)
          for name, hex_str in theme['colors'].items()}


def get_theme_reverse_lookup_color_map(theme_path):
  color_map = get_theme_color_map(theme_path)
  return {val: key for key, val in color_map.items()}


def replace_option_value_in_line(line, color_map, ignore_missed_matches=False):
  match = OPTION_PATTERN.match(line)
  if match is None:
    return line

  option_name = match.group(1)
  option_value = match.group(2)
  if option_name in IGNORED_OPTION_NAMES:
    return line

  if option_value not in color_map:
    if ignore_missed_matches:
      return line
    else:
      raise ValueError(f'Could not find color in color map: {line}')

  return line.replace(f' value="{option_value}" ',
                      f' value="{color_map[option_value]}" ')


def convert_exported_color_scheme_to_color_scheme_template(source_path, output_path, theme_path):
  color_map = get_theme_reverse_lookup_color_map(theme_path)

  with open(source_path) as f:
    input_lines = f.readlines()

  output_lines = []
  in_meta_info = False
  for line in input_lines:

    # Skip the meta info section.
    if '<metaInfo>' in line:
      in_meta_info = True
    if in_meta_info:
      if '</metaInfo>' in line:
        in_meta_info = False
      continue

    line = replace_option_value_in_line(line, color_map)
    output_lines.append(line)

  with open(output_path, 'w') as f:
    f.writelines(output_lines)


def remap_color_scheme_colors(source_path, output_path, color_map):
  with open(source_path) as f:
    input_lines = f.readlines()

  output_lines = []
  for line in input_lines:
    line = replace_option_value_in_line(line, color_map, ignore_missed_matches=True)
    output_lines.append(line)

  with open(output_path, 'w') as f:
    f.writelines(output_lines)


def build_color_scheme(source_path, output_path, theme_path, file_statuses_path):
  with open(file_statuses_path) as f:
    file_status_lines = list(filter(lambda x: x.startswith('    <option'), f.readlines()))

  with open(source_path) as f:
    input_lines = f.readlines()

  end_of_colors_index = input_lines.index('  </colors>\n')
  input_lines = (input_lines[:end_of_colors_index] +
                 file_status_lines +
                 input_lines[end_of_colors_index:])

  color_map = get_theme_color_map(theme_path)

  output_lines = []
  for line in input_lines:
    line = replace_option_value_in_line(line, color_map)
    output_lines.append(line)

  output_lines[0] = '<scheme name="Cyberpunk" version="142" parent_scheme="Darcula">'

  with open(output_path, 'w') as f:
    f.writelines(output_lines)


def convert_modified_darcula_to_darcula_template():
  convert_exported_color_scheme_to_color_scheme_template(
    source_path='modified_darcula.icls',
    output_path='darkula_template.xml',
    theme_path='modified_darkula_theme.json')


def remap_darkula_template_to_cyberpunk_template():
  remap_color_scheme_colors(
    source_path='darkula_template.xml',
    output_path='cyberpunk_template.xml',
    color_map={
      'red': 'orange',
      'orange': 'red',
      'yellow': 'blue',
      'green': 'yellow',
      'blue': 'green',
      # 'purple': 'purple',
    })


def build_cyberpunk_color_scheme():
  build_color_scheme(
    source_path='cyberpunk_template.xml',
    output_path='../../src/main/resources/cyberpunk.xml',
    theme_path='../../src/main/resources/cyberpunk.theme.json',
    file_statuses_path='file_statuses_template.xml')


def main():
  convert_modified_darcula_to_darcula_template()
  remap_darkula_template_to_cyberpunk_template()
  build_cyberpunk_color_scheme()


if __name__ == '__main__':
  main()
