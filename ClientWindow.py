import arcade
from data_packets import ConnectionAttempt, User, ConnectionState, GameState, PlayerEvent
from buttons import TextButton
from settings import *


class NameTab:
    def __init__(self, center_x, center_y, user_id, width=NAME_WIDTH, height=NAME_HEIGHT, text='DefaultText'):
        self.font = 20
        self.text = text

        self.width = width
        self.height = height

        self.x = center_x
        self.y = center_y

        self.default_color = (255, 184, 140)
        self.color = (255, 184, 140)

        self.user_id = user_id

    def set_color(self, color):
        self.color = color

    def draw(self):
        arcade.draw_rectangle_filled(self.x, self.y, self.width, self.height, self.color)

        arcade.draw_text(self.text, self.x, self.y,
                         arcade.color.BLACK, font_size=self.font,
                         width=self.width, align="center", anchor_x="center", anchor_y="center")


class ClientWindow(arcade.Window):
    def __init__(self):
        super().__init__(width=SCREEN_WIDTH, height=SCREEN_HEIGHT, title=SCREEN_TITLE)
        arcade.set_background_color(arcade.color.AMAZON)

        self.shapes = arcade.ShapeElementList()

        self.game_state = GameState(user_count=0, users=[], started=False, current_turn=None)
        self.user = None

        self.center_x = int(SCREEN_WIDTH/2)
        self.center_y = int(SCREEN_HEIGHT/2)
        self.third_line_y = int(2*SCREEN_HEIGHT/3)

        # Gradient Background:
        color1 = (26, 15, 35)
        color2 = (75, 39, 83)
        points = (0, 0), (SCREEN_WIDTH, 0), (SCREEN_WIDTH, SCREEN_HEIGHT), (0, SCREEN_HEIGHT)
        colors = (color1, color1, color2, color2)
        rect = arcade.create_rectangle_filled_with_colors(points, colors)
        self.shapes.append(rect)

        # PlayerNames:
        self.name_tabs = []
        self.name_loc = {'bot': (self.center_x, int(NAME_HEIGHT/2)),
                         'left': (int(NAME_WIDTH/2), self.third_line_y),
                         'top': (self.center_x, int(SCREEN_HEIGHT-NAME_HEIGHT/2)),
                         'right': (int(SCREEN_WIDTH-NAME_WIDTH/2), self.third_line_y)}

        # Buttons:
        self.info_btn = TextButton(center_x=SCREEN_WIDTH - BUTTON_WIDTH / 2 - MARGIN,
                                   center_y=BUTTON_HEIGHT / 2 + MARGIN,
                                   width=BUTTON_WIDTH,
                                   height=BUTTON_HEIGHT,
                                   text='Info',
                                   action_function=self.info_btn_click,
                                   face_color=arcade.color.AIR_FORCE_BLUE)
        self.burn_btn = TextButton(center_x=SCREEN_WIDTH - 5 * BUTTON_WIDTH / 2 - 3 * MARGIN,
                                   center_y=BUTTON_HEIGHT / 2 + MARGIN,
                                   width=BUTTON_WIDTH,
                                   height=BUTTON_HEIGHT,
                                   text='Burn',
                                   action_function=self.burn_btn_click,
                                   face_color=arcade.color.ALMOND)
        self.place_btn = TextButton(center_x=SCREEN_WIDTH - 3 * BUTTON_WIDTH / 2 - 2 * MARGIN,
                                    center_y=BUTTON_HEIGHT / 2 + MARGIN,
                                    width=BUTTON_WIDTH,
                                    height=BUTTON_HEIGHT,
                                    text='Place',
                                    action_function=self.place_btn_click,
                                    face_color=arcade.color.BLOND)
        self.buttons = [self.info_btn, self.burn_btn, self.place_btn]

    def place_btn_click(self):
        print('Place')

    def info_btn_click(self):
        print('info')

    def burn_btn_click(self):
        print('burn')

    def on_draw(self):
        arcade.start_render()
        self.shapes.draw()
        for n in self.name_tabs:
            n.draw()
        for b in self.buttons:
            b.draw()

        if self.game_state.user_count < 4 and not self.game_state.started:
            arcade.draw_text(f'Waiting for players...{self.game_state.user_count}/4',
                             SCREEN_WIDTH/2, SCREEN_HEIGHT/2, arcade.color.WHITE, 12,
                             align="center", anchor_x='center', anchor_y='center')

    def update_game_state(self, GS):
        # If the user numbers don't match -> update the name tabs.
        if len(self.game_state.users) != len(GS.users):
            self.update_name_tabs(GS)

        # If we are already playing -> Highlight the player whose turn it is.
        if GS.started:
            for n in self.name_tabs:
                if n.user_id == GS.current_turn.user_id:
                    n.set_color(arcade.color.ALICE_BLUE)
                else:
                    n.set_color(n.default_color)

        # Set the game state to what it is
        self.game_state = GS

    # Generator method to loop along a list with a different starting point.
    @staticmethod
    def starting_with(lst, start):
        for idx in range(len(lst)):
            yield lst[(idx + start) % len(lst)]

    def update_name_tabs(self, GS):
        self.name_tabs = []
        # Always start drawing name tabs with the client's username in the bottom:
        i = 0
        for u in self.starting_with(GS.users, GS.users.index(self.user)):
            x = list(self.name_loc.items())[i][1][0]
            y = list(self.name_loc.items())[i][1][1]
            nametab = NameTab(x, y, user_id=u.user_id, text=u.name)
            i += 1

            self.name_tabs.append(nametab)

    def update_user_data(self, user):
        self.user = user

    def on_mouse_press(self, x: float, y: float, button: int, modifiers: int):
        for b in self.buttons:
            if b.check_mouse_press(x, y):
                b.on_press()

    def on_mouse_release(self, x: float, y: float, button: int,
                         modifiers: int):
        for b in self.buttons:
            if b.pressed:
                b.on_release()

    def on_key_press(self, symbol, modifiers):
        if symbol == arcade.key.Q:
            print('left')

    def on_key_release(self, key, modifiers):
        print('RELEASE!')
