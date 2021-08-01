import arcade
import game.game_settings as settings
import os
from . import PARENT_DIR


class CardTab(arcade.Sprite):
    def __init__(self, card, loc, index, self_card=False):
        self.card = card                            # Card() object with color and number
        self.location = settings.CARD_LOCATIONS[loc][index]  # Global settings for the locations
        self.index = index                          # Store index
        self.x = self.location[0]                   # Card Tab location x
        self.y = self.location[1]                   # Card Tab location y
        self.self_card = self_card                  # Boolean to show whether the card is in the player's hands:

        # Get filepaths for the assets
        assets_path = os.path.join(PARENT_DIR, '../../../assets')
        self.col = card["color"]
        self.num = card["number"]
        filename = f'{self.col}_{self.num}.png'
        filename_question_mark = "../../assets/question_mark.png"
        filepath = os.path.join(assets_path, filename)

        # Load sprite with additional question mark texture
        super().__init__(filename=filepath, center_x=self.x, center_y=self.y)
        question_mark_texture = arcade.load_texture(os.path.join(assets_path, filename_question_mark))
        self.append_texture(question_mark_texture)

        # If the card is the player's card: show question mark texture
        if self_card:
            self.set_texture(1)
        else:
            self.set_texture(0)

        self.selected = False
        self.currently_pressed = False

    def check_mouse_press(self, x, y):
        if x > self.center_x + self.width / 2:
            return False
        if x < self.center_x - self.width / 2:
            return False
        if y > self.center_y + self.height / 2:
            return False
        if y < self.center_y - self.height / 2:
            return False
        return True

    def on_press(self):
        self.currently_pressed = True

    def on_release(self):
        self.currently_pressed = False
        self.selected = not self.selected
