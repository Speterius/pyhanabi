import arcade
from settings import *


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

    def set_face_color(self, arcade_color_obj):
        self.face_color = arcade_color_obj
        return 1

    def draw(self):
        """ Draw the button """
        arcade.draw_rectangle_filled(self.center_x, self.center_y, self.width,
                                     self.height, self.face_color)

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

        x = self.center_x
        y = self.center_y
        if not self.pressed:
            x -= self.button_height
            y += self.button_height

        arcade.draw_text(self.text, x, y,
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


class CardButton(TextButton):
    def __init__(self, center_x, center_y, card_data, action_function, card_index):
        super().__init__(center_x=center_x,
                         center_y=center_y,
                         width=CARD_WIDTH,
                         height=CARD_HEIGHT,
                         text=str(card_data[1]),
                         action_function=self.card_clicked,
                         font_size=30,
                         font_face="Arial")
        self.card_data = card_data

        self.card_color = card_data[0]
        self.card_number = card_data[1]

        self.action_function = action_function

        self.color_dict = {'blue': arcade.color.BLUE,
                           'red': arcade.color.RED,
                           'green': arcade.color.GREEN,
                           'yellow': arcade.color.YELLOW,
                           'white': arcade.color.WHITE}

        self.face_color = self.color_dict[self.card_color]

        self.card_index = card_index
        self.selected = False

    def card_clicked(self):
        print("Clicked Card:  " + self.card_color + str(self.card_number))
        self.selected = True

    def on_release(self):
        super().on_release()
        self.card_clicked()
        self.action_function()
