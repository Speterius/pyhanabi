SCREEN_WIDTH = 600

MID_SPACING_X = [30, 110, 190, 270]
MID_SPACING_RIGHT = [SCREEN_WIDTH - MID_SPACING_X[i] for i in range(-1, -5, -1)]


def hex_to_rgb(h):
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))