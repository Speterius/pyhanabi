import arcade
import os
from arcade.draw_commands import load_texture
from game_logic import Card
from settings import *

PARENT_DIR = os.path.abspath(os.path.dirname(__file__))


def hex_to_rgb(h):
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))


class CardTab(arcade.Sprite):
    def __init__(self, card, loc, index, self_card=False):
        assert type(card) == Card
        assert loc in ['bot', 'left', 'top', 'right']
        assert 0 <= index <= 3

        self.card = card                            # Card() object with color and number
        self.location = CARD_LOCATIONS[loc][index]  # Global settings for the locations
        self.x = self.location[0]                   # Card Tab location x
        self.y = self.location[1]                   # Card Tab location y
        self.self_card = self_card                  # Boolean to show whether the card is in the player's hands:
        self.original_scale = 0.65                  # Scaling the image.

        # Get filepaths for the assets
        assets_path = os.path.join(PARENT_DIR, 'assets')
        filename = f'{self.card.color}_{self.card.number}.png'
        filename_question_mark = "question_mark.png"
        filepath = os.path.join(assets_path, filename)

        # Load sprite with additional question mark texture
        super().__init__(filename=filepath, scale=self.original_scale, center_x=self.x, center_y=self.y)
        question_mark_texture = load_texture(os.path.join(assets_path, filename_question_mark))
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

    def on_press_down(self):
        self.currently_pressed = True

    def on_release_up(self):
        self.currently_pressed = False

        if not self.selected:
            self.selected = True
            self._set_scale(0.75)
        else:
            self.selected = False
            self._set_scale(self.original_scale)


class NameTab:
    def __init__(self, center_x, center_y, width=NAME_WIDTH, height=NAME_HEIGHT, text='DefaultText'):
        self.font = 20
        self.text = text

        self.width = width
        self.height = height

        self.center_x = center_x
        self.center_y = center_y

        self.highlight_color: arcade.Color = hex_to_rgb('80d0c7')
        self.color: arcade.Color = hex_to_rgb('13547a')

        self.highlight = False

    def draw(self):
        if self.highlight:
            arcade.draw_rectangle_filled(center_x=self.center_x, center_y=self.center_y,
                                         width=self.width, height=self.height,
                                         color=self.highlight_color)
        else:
            arcade.draw_rectangle_filled(center_x=self.center_x, center_y=self.center_y,
                                         width=self.width, height=self.height,
                                         color=self.color)

        arcade.draw_text(self.text, self.center_x, self.center_y,
                         color=arcade.color.BLACK, font_size=self.font,
                         width=self.width, align="center", anchor_x="center", anchor_y="center")


class TextButton:
    def __init__(self,
                 center_x, center_y,
                 width, height,
                 text,
                 action_function,
                 font_size=18,
                 font_face="Arial",
                 face_color=arcade.color.LIGHT_GRAY,
                 highlight_color=arcade.color.WHITE,
                 shadow_color=arcade.color.GRAY,
                 button_height=2):
        self.center_x = center_x
        self.center_y = center_y
        self.width = width
        self.height = height
        self.text = text
        self.font_size = font_size
        self.font_face = font_face
        self.pressed = False
        self.face_color = face_color
        self.highlight_color = highlight_color
        self.shadow_color = shadow_color
        self.button_height = button_height

        self.action_function = action_function

    def set_face_color(self, color: arcade.Color):
        self.face_color = color
        return 1

    def draw(self):
        arcade.draw_rectangle_filled(self.center_x, self.center_y, self.width, self.height, self.face_color)

        if not self.pressed:
            color = self.shadow_color
        else:
            color = self.highlight_color

        # Bottom horizontal
        arcade.draw_line(self.center_x - self.width / 2, self.center_y - self.height / 2,
                         self.center_x + self.width / 2, self.center_y - self.height / 2,
                         color, self.button_height)

        # Right vertical
        arcade.draw_line(self.center_x + self.width / 2, self.center_y - self.height / 2,
                         self.center_x + self.width / 2, self.center_y + self.height / 2,
                         color, self.button_height)

        if not self.pressed:
            color = self.highlight_color
        else:
            color = self.shadow_color

        # Top horizontal
        arcade.draw_line(self.center_x - self.width / 2, self.center_y + self.height / 2,
                         self.center_x + self.width / 2, self.center_y + self.height / 2,
                         color, self.button_height)

        # Left vertical
        arcade.draw_line(self.center_x - self.width / 2, self.center_y - self.height / 2,
                         self.center_x - self.width / 2, self.center_y + self.height / 2,
                         color, self.button_height)

        text_x = self.center_x
        text_y = self.center_y
        if not self.pressed:
            text_x -= self.button_height
            text_y += self.button_height

        arcade.draw_text(self.text, text_x, text_y,
                         arcade.color.BLACK, font_size=self.font_size,
                         width=self.width, align="center",
                         anchor_x="center", anchor_y="center")

    def on_press(self):
        self.pressed = True

    def on_release(self):
        self.pressed = False
        self.action_function()

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
