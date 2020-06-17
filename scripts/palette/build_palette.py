""" A script for building the theme's color palette.

Uses the cylindrical LAB color space, also known as the LCH color space for
lightness, chroma, hue. The generated palette has colors varying linearly in
lightness (top to bottom), with chroma values at equidistant radial
values (with the base chroma being zero, meaning the greys, and the different
chroma level being the grouped patches varying from left to right), and with
hues at equidistant angle (varying left to right within each group). The
generated palette is then saved as an SVG image.

For some colors, when converting from LAB space to RGB space, the RGB values
can exceed the max of the valid 8-bit range which is 255. When this happens
those channel values will be clamped at down to 255 and the color patch that is
drawn in the SVG will have a small square within it indicating that that that
color was clipped. The shade of that inner square indicates how much it was
clipped by, with white meaning that it was barely clipped, and a shade of grey
meaning that it was only clipped by a few bit values.

Along the top of the color palette will be a row colors that have the maximum
possible lightness value before clipping for that column's specific chroma
and hue.

The cyberpunk blue (#00F0FF) was taken from this Cyberpunk 2077 picture:
https://www.facebook.com/CyberpunkGame/photos/a.384927278254777/2913293268751486/

The cyberpunk red (#FF5952) and cyberpunk orange (#FFBD7D) were taken from the
red and orange UI elements in this Cyberpunk 2077 picture:
https://www.facebook.com/CyberpunkGame/photos/a.384927278254777/2363885590358926/

Cyberpunk blue: #00F0FF (base color)
  L: 86.76833059325895
  C: 46.35777632716608
  H: -2.6792770452854326

Cyberpunk red: #FF5952
  L: 60.79840451387447
  C: 73.58963490378852
  H: 0.5563143684433922

Cyberpunk orange: #FFBD7D
  L: 81.36795524748165
  C: 44.66210718064023
  H: 1.1903739435486187

The cyberpunk blue was used as the base color to generate a palette, and then
the following colors were chosen for the theme. The cyberpunk red looked better
than any of the reds in the palette so it was used instead of a palette color
(it's the only color used that was not in the generated palette). To the right
of the colors are listed their lightness (L), chroma (C), and hue (H) indexes
in the palette, 0 lightness being black, 0 chroma being grey, 0 hue being the
hue of the base color (cyberpunk blue):

  red:       #FF5952, (cyberpunk red)
  orange:    #FFC07A, L: max, C: 2, H: 20 (similar to cyberpunk orange)
  yellow:    #FFE68D, L: max, C: 2, H: 22
  green:     #0FC166, L: 21,  C: 3, H: 27
  lightBlue: #00E0EF, L: 26,  C: 2, H: 0 (a darker version of cyberpunk blue)
  darkBlue:  #1DBBFF, L: max, C: 2, H: 4
  purple:    #D59BE8, L: 23,  C: 2, H: 10
  pink:      #FFAEF4, L: max, C: 2, H: 11

"""
import math

from colormath.color_conversions import convert_color
from colormath.color_objects import LabColor, sRGBColor
import numpy as np
import svgwrite

# The base color that the palette is generated from.
BASE_COLOR = '00f0ff'  # Cyberpunk blue.

# The number of different lightness values, with the lowest value being 0 and
# the highest value being 100. Use 33 (or any (2^n) + 1) to generate a palette
# with easily divisible lightness values (halves, and halves of halves), or use
# 16 to get the base color (#00F0FF) to be one of the discrete (non-max) color
# values.
NUM_L = 33

# The number of different chroma values.
NUM_C = 5

# Which index in the different chromas will match the base color's chroma.
# E.g. If this is set to 2 when NUM_C is 5, the middle chroma will have the
# base color's chroma:
#   chroma 0: greys
#   chroma 1: half the base color's chroma
#   chroma 2: the base color's chroma
#   chroma 3: 3/2 the base color's chroma
#   chroma 4: double the base color's chroma
CHROMA_INDEX_OF_BASE_COLOR = 2

# The number of different hues. The base color's hue will be one of the hues
# and the other hues will equally divide the 360 degree range.
NUM_H = 32

# The size of the color patches in the SVG image, and the size of the inner
# squares that indicate if that color was clipped.
PATCH_SQUARE_SIZE = (50, 50)
CLIP_SQUARE_SIZE = (PATCH_SQUARE_SIZE[0] // 5, PATCH_SQUARE_SIZE[1] // 5)
CLIP_SQUARE_OFFSET = ((PATCH_SQUARE_SIZE[0] - CLIP_SQUARE_SIZE[0]) // 2,
                      (PATCH_SQUARE_SIZE[1] - CLIP_SQUARE_SIZE[1]) // 2)

OUTPUT_PATH = 'palette.svg'

# This is the standard illuminant value used by sRGB, 6500 Kelvin daylight.
ILLUMINANT = 'd65'


def draw_svg(colors):
  width = len(colors) * PATCH_SQUARE_SIZE[0]
  height = len(colors[0]) * PATCH_SQUARE_SIZE[1]
  dwg = svgwrite.Drawing(OUTPUT_PATH, size=(width, height), profile='tiny')
  for hue_index, hue_shades in enumerate(colors):
    for shade_index, color in enumerate(hue_shades):
      hex_str, clip_amount = color
      x = hue_index * PATCH_SQUARE_SIZE[0]
      y = height - ((shade_index + 1) * PATCH_SQUARE_SIZE[1])  # darker colors at the bottom.
      dwg.add(dwg.rect((x, y), PATCH_SQUARE_SIZE, fill=hex_str))

      # If a color channel was clipped by more than 1 / 512, that means the
      # channel value would have at least rounded up to be out of range.
      if clip_amount > 1 / 512:

        if clip_amount >= 1 / 32:
          fill = '#000'  # It was clipped by more than 8 bits.
        elif clip_amount >= 1 / 64:
          fill = '#666'  # It was clipped by between 4 and 8 bits.
        elif clip_amount >= 1 / 128:
          fill = '#999'  # It was clipped by between 3 and 4 bits.
        elif clip_amount >= 1 / 256:
          fill = '#ccc'  # It was clipped by between 1 and 2 bits.
        else:
          fill = '#fff'  # It was clipped by between .5 and 1 bits.

        x += CLIP_SQUARE_OFFSET[0]
        y += CLIP_SQUARE_OFFSET[1]
        dwg.add(dwg.rect((x, y), CLIP_SQUARE_SIZE, fill=fill))

  dwg.save()


def ab_to_ch(a, b):
  c = (a ** 2 + b ** 2) ** 0.5
  h = math.atan2(b, a)
  return c, h


def ch_to_ab(c, h):
  a = c * math.cos(h)
  b = c * math.sin(h)
  return a, b


def get_clip_amount(rgb_color):
  return max(0, rgb_color.rgb_r - 1, rgb_color.rgb_g - 1, rgb_color.rgb_b - 1)


def get_clamped_rgb_color(rgb_color):
  return sRGBColor(rgb_color.clamped_rgb_r,
                   rgb_color.clamped_rgb_g,
                   rgb_color.clamped_rgb_b)


def lch_to_hex_str_and_clip_amount(l, c, h):
  a, b = ch_to_ab(c, h)
  lab_color = LabColor(l, a, b, illuminant=ILLUMINANT)
  rgb_color = convert_color(lab_color, sRGBColor)
  clip_amount = get_clip_amount(rgb_color)
  clamped_rgb_color = get_clamped_rgb_color(rgb_color)
  hex_str = clamped_rgb_color.get_rgb_hex()
  return hex_str, clip_amount


def get_lightest_unclipped_color(c, h):
  a, b = ch_to_ab(c, h)
  if c == 0:
    return '#ffffff', 0

  # Run a binary search to find the lightest unclipped color.
  max_rgb_color = None
  cur_l = 50
  delta = 25
  while delta > 0:
    lab_color = LabColor(cur_l, a, b, illuminant=ILLUMINANT)
    rgb_color = convert_color(lab_color, sRGBColor)
    if get_clip_amount(rgb_color) == 0:
      max_rgb_color = rgb_color
      cur_l += delta
    else:
      cur_l -= delta

    delta /= 2

  hex_str = max_rgb_color.get_rgb_hex()
  return hex_str, 0


def get_shades(start_l, end_l, num_l, c, h):
  colors = []
  for l in np.linspace(start_l, end_l, num_l):
    colors.append(lch_to_hex_str_and_clip_amount(l, c, h))
  colors.append(get_lightest_unclipped_color(c, h))
  return colors


def get_hues(start_l, end_l, num_l, c, start_h, num_h):
  colors = []
  for h in np.linspace(start_h, start_h + math.tau, num_h, endpoint=False):
    colors.append(get_shades(start_l, end_l, num_l, c, h))
  return colors


def get_chromas(start_l, end_l, num_l, start_c, end_c, num_c, start_h, num_h):
  colors = []
  for c in np.linspace(start_c, end_c, num_c):
    cur_num_h = num_h if c > 0 else 1
    colors.extend(get_hues(start_l, end_l, num_l, c, start_h, cur_num_h))
  return colors


def get_palette_colors(base_color, num_l, num_c, num_h, chroma_index_of_base_color):
  rgb_color = sRGBColor.new_from_rgb_hex(BASE_COLOR)
  lab_color = convert_color(rgb_color, LabColor)
  l, a, b = lab_color.get_value_tuple()
  c, h = ab_to_ch(a, b)

  print('Base color:', base_color)
  print('L:', l)
  print('C:', c)
  print('H:', h)

  start_l = 0
  end_l = 100
  start_c = 0
  end_c = c * (num_c - 1) / chroma_index_of_base_color
  start_h = h

  return get_chromas(start_l, end_l, num_l,
                     start_c, end_c, num_c,
                     start_h, num_h)


def print_closest_color(colors, target_color):
  target_rgb = sRGBColor.new_from_rgb_hex(target_color)
  min_diff = 255 * 3
  closest_hex_str = None
  stats = None
  for hue_index, shades in enumerate(colors):
    for shade_index, color in enumerate(shades):
      hex_str, clip_amount = color
      if not clip_amount:
        color_rgb = sRGBColor.new_from_rgb_hex(hex_str)
        r_diff = abs(target_rgb.rgb_r - color_rgb.rgb_r)
        g_diff = abs(target_rgb.rgb_g - color_rgb.rgb_g)
        b_diff = abs(target_rgb.rgb_b - color_rgb.rgb_b)
        diff = r_diff + g_diff + b_diff
        if diff < min_diff:
          min_diff = diff
          closest_hex_str = hex_str
          stats = (diff, hue_index, shade_index)
  print('Closest color to:', target_color, closest_hex_str,
        ' - diff, hue, shade:', stats)


def draw_palette():
  colors = get_palette_colors(BASE_COLOR, NUM_L, NUM_C, NUM_H, CHROMA_INDEX_OF_BASE_COLOR)
  draw_svg(colors)
  print('Colors:', colors)

  # Print how close the closest color in the palette is to a target color,
  # for when trying to generate palette that matches several colors.
  target_colors = (
    ('Blue', '00F0FF'),
    ('Red', 'FF5952'),
    ('Orange', 'FFBD7D'),
  )
  for name, hex_str in target_colors:
    print(name)
    print_closest_color(colors, hex_str)


def draw_hues_for_color(base_color_hex_str, num_hues=10):
  """Draws a palette of colors that only vary in hue.

  The base color's hue is used as one of the hues and the other hues will
  evenly divide the 360 degree space. All colors will use the lightness and
  chroma values of the base color.
  """
  rgb_color = sRGBColor.new_from_rgb_hex(base_color_hex_str)
  lab_color = convert_color(rgb_color, LabColor)
  l, a, b = lab_color.get_value_tuple()
  c, h = ab_to_ch(a, b)
  hues = []
  for cur_h in np.linspace(h, h + math.tau, num_hues, endpoint=False):
    hues.append(lch_to_hex_str_and_clip_amount(l, c, cur_h))
  draw_svg([hues])


def main():
  draw_palette()

  # draw_hues_for_color('FF5952')


if __name__ == '__main__':
  main()
