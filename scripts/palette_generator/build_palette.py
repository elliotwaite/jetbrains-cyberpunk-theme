import collections
import json

from colormath.color_conversions import convert_color
from colormath.color_objects import LabColor, sRGBColor
import numpy as np

ILLUMINANT = 'd65'
GREYSCALE_SHADES = 33
JSON_INDENT = '  '


def get_greyscale():
  colors = []
  for lightness_index, lightness in enumerate(np.linspace(0, 100, num=GREYSCALE_SHADES)):
    lab_color = LabColor(lightness, 0, 0, illuminant=ILLUMINANT)
    rgb_color = convert_color(lab_color, sRGBColor)
    hex_str = rgb_color.get_rgb_hex()

    if lightness == 0:
      name = 'black'
    elif lightness == 100:
      name = 'white'
    else:
      name = f'grey{lightness_index}'

    colors.append((name, hex_str))

  return colors


def print_colors(colors):
  theme = {'colors': collections.OrderedDict()}
  for (name, hex_str) in colors:
    theme['colors'][name] = hex_str
  print(json.dumps(theme, indent=JSON_INDENT))


def main():
  greyscale = get_greyscale()
  print_colors(greyscale)


if __name__ == '__main__':
  main()
