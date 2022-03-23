import math

from colormath.color_conversions import convert_color
from colormath.color_objects import LabColor, sRGBColor

# This is the standard illuminant value used by sRGB, 6500 Kelvin daylight.
ILLUMINANT = 'd65'

TARGET_LIGHTNESS_COLOR = '#CACACA'
# TARGET_LIGHTNESS_COLOR = '#00f0ff'

ORIGINAL_COLORS = [
    '#F3505C',
    '#FFC07A',
    '#EEDB85',
    '#51F66F',
    '#00F0FF',
    '#368AEC',
    '#A186E1',
    '#D867C6',
    '#FFAEF4',
]


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
    return sRGBColor(rgb_color.clamped_rgb_r, rgb_color.clamped_rgb_g, rgb_color.clamped_rgb_b)


def lch_to_hex_str_and_clip_amount(l, c, h):
    a, b = ch_to_ab(c, h)
    lab_color = LabColor(l, a, b, illuminant=ILLUMINANT)
    rgb_color = convert_color(lab_color, sRGBColor)
    clip_amount = get_clip_amount(rgb_color)
    clamped_rgb_color = get_clamped_rgb_color(rgb_color)
    hex_str = clamped_rgb_color.get_rgb_hex()
    return hex_str, clip_amount


def print_lightness_matched_colors():
    target_rgb_color = sRGBColor.new_from_rgb_hex(TARGET_LIGHTNESS_COLOR)
    target_lab_color = convert_color(target_rgb_color, LabColor, target_illuminant=ILLUMINANT)
    target_l = target_lab_color.lab_l

    for original_color in ORIGINAL_COLORS:
        rgb_color = sRGBColor.new_from_rgb_hex(original_color)
        lab_color = convert_color(rgb_color, LabColor)
        l, a, b = lab_color.get_value_tuple()
        c, h = ab_to_ch(a, b)
        hex_str, clip_amount = lch_to_hex_str_and_clip_amount(target_l, c, h)
        print(hex_str, clip_amount)


def main():
    print_lightness_matched_colors()


if __name__ == '__main__':
    main()
