# Number of allowed players
MAX_PLAYERS = 2

# Game Window Settings
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_TITLE = 'PS Hanabi'

# GUI Element Settings
NAME_WIDTH = 140
NAME_HEIGHT = 26

MARGIN = 5

BUTTON_WIDTH = 70
BUTTON_HEIGHT = 70

BOT_ROW = 80
MID_ROW = int(2*SCREEN_HEIGHT/3) - 20
TOP_ROW = SCREEN_HEIGHT-85

X_SPACING = 60

SPACING_BOT = [SCREEN_WIDTH/2-int(2*X_SPACING), SCREEN_WIDTH/2-int(0.67*X_SPACING), SCREEN_WIDTH/2+int(0.67*X_SPACING), SCREEN_WIDTH/2+int(2*X_SPACING)]
SPACING_TOP = SPACING_BOT
SPACING_LEFT = [30, 105, 180, 255]
SPACING_RIGHT = [SCREEN_WIDTH - SPACING_LEFT[i] for i in range(-1, -5, -1)]

CARD_LOCATIONS = {'bot': [(SPACING_BOT[0], BOT_ROW),
                          (SPACING_BOT[1], BOT_ROW),
                          (SPACING_BOT[2], BOT_ROW),
                          (SPACING_BOT[3], BOT_ROW)],

                  'left': [(SPACING_LEFT[0], MID_ROW),
                           (SPACING_LEFT[1], MID_ROW),
                           (SPACING_LEFT[2], MID_ROW),
                           (SPACING_LEFT[3], MID_ROW)],

                  'top': [(SPACING_TOP[0], TOP_ROW),
                          (SPACING_TOP[1], TOP_ROW),
                          (SPACING_TOP[2], TOP_ROW),
                          (SPACING_TOP[3], TOP_ROW)],

                  'right': [(SPACING_RIGHT[0], MID_ROW),
                            (SPACING_RIGHT[1], MID_ROW),
                            (SPACING_RIGHT[2], MID_ROW),
                            (SPACING_RIGHT[3], MID_ROW)]}
