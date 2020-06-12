from colormath.color_conversions import convert_color
from colormath.color_objects import LabColor, sRGBColor


def get_greyscale_equivalent(hex_str):
  rgb_color = sRGBColor.new_from_rgb_hex(hex_str)
  lab_color = convert_color(rgb_color, LabColor)
  lab_color.lab_a = 0
  lab_color.lab_b = 0
  grey_rgb_color = convert_color(lab_color, sRGBColor)
  return grey_rgb_color.get_rgb_hex()


def get_alternative_hues(hex_str, num_hues=10):
  rgb_color = sRGBColor.new_from_rgb_hex(hex_str)
  lab_color = convert_color(rgb_color, LabColor)
  lab_color.lab_a = 0
  lab_color.lab_b = 0
  grey_rgb_color = convert_color(lab_color, sRGBColor)
  return grey_rgb_color.get_rgb_hex()


def main():
  print(get_greyscale_equivalent('848504'))


if __name__ == '__main__':
  main()
