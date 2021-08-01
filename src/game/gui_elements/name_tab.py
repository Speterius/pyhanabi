from . import hex_to_rgb
import arcade
import game.game_settings as settings


class NameTab:
    def __init__(self, center_x, center_y, width=settings.NAME_WIDTH, height=settings.NAME_HEIGHT, text='DefaultText'):
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

    def set_highlight(self, foo: bool):
        self.highlight = foo
