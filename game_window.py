import arcade
from packets import GameStateUpdate
from gui_elements import NameTab, TextButton, CardTab, CardTabList
from settings import *
from game_logic import CardPull, CardBurned, CardPlaced, NextTurn, InfoUsed


# noinspection PyArgumentList
class GameWindow(arcade.Window):
    def __init__(self, client):
        super().__init__(width=SCREEN_WIDTH, height=SCREEN_HEIGHT, title=SCREEN_TITLE)
        arcade.set_background_color(arcade.color.AMAZON)
        # Client used to send events to the server and to receive GS (GameState) updates.
        self.client = client
        self.GS = None
        self.connection: bool = False
        self.player_name: str = None
        self.player_id: int = None

        # GUI Elements
        self.shapes = arcade.ShapeElementList()
        self.center_x = int(SCREEN_WIDTH/2)
        self.center_y = int(SCREEN_HEIGHT/2)
        self.third_line_y = int(2*SCREEN_HEIGHT/3)+50

        # Gradient Background:
        self.generate_gradient_background()

        # Player Names and Locations:
        self.name_tabs = {}                                                     # store NameTab objects
        self.name_loc = {'bot': (self.center_x, int(NAME_HEIGHT/2)),            # locations of NameTab objects
                         'left': (int(NAME_WIDTH/2), self.third_line_y),
                         'top': (self.center_x, int(SCREEN_HEIGHT-NAME_HEIGHT/2)),
                         'right': (int(SCREEN_WIDTH-NAME_WIDTH/2), self.third_line_y)}

        self.player_locations = {}                                              # KEY: int   VALUE: (x, y)

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

        # Cards:
        self.cards_generated = False
        self.card_tab_list = CardTabList()          # Card Tab arcade.Spritelist

        self.selected_card_tab = None

    def generate_gradient_background(self):
        color1 = (26, 15, 35)
        color2 = (75, 39, 83)
        points = (0, 0), (SCREEN_WIDTH, 0), (SCREEN_WIDTH, SCREEN_HEIGHT), (0, SCREEN_HEIGHT)
        colors = (color1, color1, color2, color2)
        rect = arcade.create_rectangle_filled_with_colors(points, colors)
        self.shapes.append(rect)

    def draw_start_screen(self):
        if not self.connection:
            arcade.draw_text(f'Waiting for server connection...',
                             SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2, arcade.color.WHITE, 14,
                             align="center", anchor_x='center', anchor_y='center')

        if self.GS is not None:
            if len(self.GS.players.keys()) < MAX_PLAYERS:
                arcade.draw_text(f'Waiting for players...{len(self.GS.players)}/{MAX_PLAYERS}',
                                 SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2, arcade.color.WHITE, 14,
                                 align="center", anchor_x='center', anchor_y='center')

    def on_draw(self):
        arcade.start_render()

        # Draw purple background:
        self.shapes.draw()

        # If the game hasn't started yet, draw the connection screen:
        if self.GS is None or not self.GS.started:
            self.draw_start_screen()

        # If the game has started, draw the UI elements:
        else:
            # 2) Player Names
            for _, n in self.name_tabs.items():
                n.draw()

            # 3) Buttons
            for b in self.buttons:
                b.draw()

            # 4) Texts
            arcade.draw_text(f'INFO POINTS: {self.GS.info_points}',
                             SCREEN_WIDTH - 100, SCREEN_HEIGHT / 2, arcade.color.WHITE, 14,
                             align="center", anchor_x='center', anchor_y='center')

            arcade.draw_text(f'LIFE POINTS: {self.GS.life_points}',
                             SCREEN_WIDTH - 100, SCREEN_HEIGHT / 2 - 50, arcade.color.WHITE, 14,
                             align="center", anchor_x='center', anchor_y='center')

            # 5) Draw Cards
            self.card_tab_list.draw()

            try:
                if self.GS.started:
                    arcade.draw_text('The game has started', SCREEN_WIDTH/4, SCREEN_HEIGHT/4, arcade.color.WHITE)
                else:
                    arcade.draw_text('GS.started is false', SCREEN_WIDTH / 4, SCREEN_HEIGHT / 4, arcade.color.WHITE)
            except:
                pass

    def generate_card_tabs(self, player_hands):

        # Loop through the players and generate the cards tabs GUI elements:
        for player_id in player_hands:

            # If the card is in the client's hand: hide the sprite (self_card).
            self_card = self.player_id == player_id
            loc = self.player_locations[player_id]

            # Loop through the 4 cards and generate each Sprite and add to the SpriteList:
            for card_index, card in player_hands[player_id].items():
                card_tab = CardTab(card=card, loc=loc, index=card_index, self_card=self_card)
                self.card_tab_list.append(card_tab)

    def update_name_tabs(self, players):

        # 1) Map players to locations on the game window:
        position_list = list(self.name_loc.keys())      # This will return ['bot', 'left', 'top', 'right']
        player_locations = dict()                       # Empty dict to store location mapping:

        for i in range(len(players)):
            player_locations[(self.player_id+i) % len(players)] = position_list[i]

        # 2) Update the Name Tabs list:
        self.name_tabs = {}

        for player_id, location in player_locations.items():

            x = self.name_loc[location][0]
            y = self.name_loc[location][1]
            name = players[player_id]

            nametab = NameTab(center_x=x, center_y=y, text=name)
            self.name_tabs[player_id] = nametab

        self.player_locations = player_locations

    def update_game_state(self, game_state_update: GameStateUpdate):

        if self.GS is None:
            self.GS = game_state_update
            self.update_name_tabs(game_state_update.players)
            return

        # If the players numbers have changed:
        if len(self.GS.players) != len(game_state_update.players):
            self.update_name_tabs(game_state_update.players)

        # If we are already playing:
        if game_state_update.started:
            # Make the card tabs at the start of the game.
            if not self.cards_generated:
                self.generate_card_tabs(game_state_update.player_hands)
                self.cards_generated = True

            # Highlight the player name tab whose turn it is:
            for player_id, nametab in self.name_tabs.items():
                if player_id == game_state_update.current_player:
                    nametab.set_highlight(True)
                else:
                    nametab.set_highlight(False)

            # todo: update card tabs

            # todo: update discard pile

            # todo: update table stash

            # todo: update info point and life point texts

        # Update the current GS object.
        self.GS = game_state_update

    def get_card_selection(self):

        if self.selected_card_tab is None:
            return None, None

        card = self.selected_card_tab.card
        card_position = self.selected_card_tab.index

        return card, card_position

    def on_mouse_press(self, x: float, y: float, button: int, modifiers: int):
        for b in self.buttons:
            if b.check_mouse_press(x, y):
                b.on_press()

        for c in self.card_tab_list:
            if c.self_card:
                if c.check_mouse_press(x, y):
                    c.on_press()

    def on_mouse_release(self, x: float, y: float, button: int, modifiers: int):
        for b in self.buttons:
            if b.pressed:
                b.on_release()

        for i, c in enumerate(self.card_tab_list):
            if c.self_card and c.currently_pressed:

                c.on_release()

                if c.selected:
                    self.selected_card_tab = c
                    self.delete_other_selections(selection=i)

    def delete_other_selections(self, selection):
        for i, c in enumerate(self.card_tab_list):
            if i == selection:
                continue
            else:
                c.set_selection(False)

    def on_key_press(self, symbol, modifiers):
        if symbol == arcade.key.Q:
            print('Q')

    def on_key_release(self, key, modifiers):
        print('KEY RELEASE!')
    #
    #
    # PLAYER EVENTS:
    #
    # _____________

    def info_btn_click(self):
        print("clicked info button")
        event = InfoUsed(self.player_id)

        print("sending event:", event)
        self.client.send_game_event(event)

    def burn_btn_click(self):
        card, card_position = self.get_card_selection()

        if card is not None and card_position is not None:

            event = CardBurned(self.player_id, card, card_position)
            self.client.send_game_event(event)

        else:
            print('Select card first.')

    def place_btn_click(self):
        card, card_position = self.get_card_selection()

        if card is not None and card_position is not None:

            event = CardPlaced(self.player_id, card, card_position)
            self.client.send_game_event(event)

        else:
            print('Select card first.')

    def pull_card_click(self):
        event = CardPull(self.player_id)
        self.client.send_game_event(event)

    def next_turn_click(self):
        event = NextTurn(self.player_id)
        self.client.send_game_event(event)
