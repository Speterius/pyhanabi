import arcade
import time
from packets import GameStateUpdate, CardPlaced, CardBurned, CardPull, InfoUsed, NextTurn
from gui_elements import NameTab, TextButton, CardTab, CardTabList
from settings import *


class GameWindow(arcade.Window):
    def __init__(self, client):
        super().__init__(width=SCREEN_WIDTH, height=SCREEN_HEIGHT, title=SCREEN_TITLE)
        arcade.set_background_color(arcade.color.AMAZON)

        self.client = client            # Client used to send events to the server and to receive game state updates.
        self.GS = None                  # Current game state

        self.connection: bool = False   # Server connection
        self.player_name: str = ""      # Player's name
        self.player_id = None           # Player's integer id assigned by the server

        # GUI Elements:
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
        self.pull_btn = TextButton(center_x=BUTTON_WIDTH / 2 + MARGIN,
                                   center_y=BUTTON_HEIGHT / 2 + MARGIN,
                                   width=BUTTON_WIDTH,
                                   height=BUTTON_HEIGHT,
                                   text='PULL',
                                   action_function=self.pull_btn_click,
                                   face_color=arcade.color.ORANGE)
        self.next_btn = TextButton(center_x=3 * BUTTON_WIDTH / 2 + 2 * MARGIN,
                                   center_y=BUTTON_HEIGHT / 2 + MARGIN,
                                   width=BUTTON_WIDTH,
                                   height=BUTTON_HEIGHT,
                                   text='NEXT',
                                   action_function=self.next_btn_click,
                                   face_color=arcade.color.BARBIE_PINK)

        self.buttons = [self.info_btn, self.burn_btn, self.place_btn, self.pull_btn, self.next_btn]

        # Cards:
        self.cards_generated = False
        self.card_tab_list = CardTabList()          # Card Tab arcade.Spritelist
        self.selected_card_tab = None

        # Message Pop-up:
        self.message_text = None        # text to display as a message
        self.message_timer = None       # time of the message popup start
        self.message_duration = 2.0     # seconds for the message to disappear

        # Some game state logic on the client side:
        self.action_done = False

        # Keep track of the top card in the discard pile and the number of cards here to keep track.
        self.discard_pile_card_tabs_top = None
        self.discard_pile_size = 0

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
                             SCREEN_WIDTH - 100, SCREEN_HEIGHT / 2 - 50, arcade.color.WHITE, 14,
                             align="center", anchor_x='center', anchor_y='center')

            arcade.draw_text(f'LIFE POINTS: {self.GS.life_points}',
                             SCREEN_WIDTH - 70, SCREEN_HEIGHT / 2 - 100, arcade.color.WHITE, 14,
                             align="center", anchor_x='center', anchor_y='center')

            # 5) Draw Cards
            self.card_tab_list.draw()

            # 6) draw highlights:
            if self.selected_card_tab is not None:
                l, r, t, b = self.selected_card_tab.get_lrtb()
                arcade.draw_lrtb_rectangle_outline(l, r, t, b, arcade.color.WHITE, border_width=2)

            # 7) Display message:
            self.draw_message()

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

    def has_four_cards(self):
        for idx, card in self.GS.player_hands[self.player_id].items():
            if card["color"] == "empty":
                return False
        return True

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

            # todo: update the card tabs. Make sure they are in sync with server game state

            # todo: update discard pile
            self.discard_pile_size = len(game_state_update.discard_pile)

            # todo: update table stash

        # Update the current GS object.
        self.GS = game_state_update

    def get_card_selection(self):

        """ Return the card dict and the index of the card that is being selected.
            Returns None for both if nothing is selected. """

        if self.selected_card_tab is None:
            return None, None, None

        card = self.selected_card_tab.card
        card_position = self.selected_card_tab.index

        return card, card_position, self.selected_card_tab

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

        released_on_card = []
        for i, c in enumerate(self.card_tab_list):
            if c.self_card and c.currently_pressed:
                released_on_card.append(1)
                c.on_release()

                if c.selected:
                    self.filter_selections(exception=i)

        if not released_on_card:
            self.filter_selections()

        _, index, _ = self.get_card_selection()

    def filter_selections(self, exception=None):
        for i, c in enumerate(self.card_tab_list):
            if i == exception:
                self.selected_card_tab = c
            else:
                c.set_selection(False)
        if exception is None:
            self.selected_card_tab = None

    def _player_event(btn_click):
        """ This is a decorator for all player events to check whether it is the player's turn"""
        def check_current_player(self):

            if self.player_id != self.GS.current_player:
                self.show_message('Not your turn.')
                return

            btn_click(self)

        return check_current_player

    def _player_action(btn_click):
        """ This is a decorator for the three action events that can only be done once per turn. """
        def check_action_done(self):

            if self.action_done:
                self.show_message('Already did your action. Click NEXT or PULL card.')
                return

            btn_click(self)

        return check_action_done

    def _uses_card(btn_click):
        """ This is a decorator for the two action events that needs a valid card selection."""
        def check_card_selection(self):

            card, card_position, _ = self.get_card_selection()
            if card is not None and card_position is not None:

                btn_click(self, card, card_position)

            else:
                self.show_message('Select a card before using BURN.')

        return check_card_selection

    @_player_event
    @_player_action
    def info_btn_click(self):

        """ Player event: When the INFO button is clicked."""

        event = InfoUsed(self.player_id)
        self.client.send_game_event(event.to_bytes())

        self.action_done = True

    @_player_event
    @_player_action
    @_uses_card
    def burn_btn_click(self, card=None, card_position=None):

        """ Player event: When the BURN button is clicked."""

        event = CardBurned(self.player_id, card, card_position)
        self.client.send_game_event(event.to_bytes())

        self.action_done = True

    @_player_event
    @_player_action
    @_uses_card
    def place_btn_click(self, card=None, card_position=None):

        """ Player event: When the PLACE button is clicked."""

        event = CardPlaced(self.player_id, card, card_position)
        self.client.send_game_event(event.to_bytes())

        self.action_done = True

    @_player_event
    def pull_btn_click(self):

        """ Player event: When the PULL button is clicked."""
        if self.has_four_cards():
            self.show_message('You already have all cards.')
            return

        event = CardPull(self.player_id)
        self.client.send_game_event(event.to_bytes())

    @_player_event
    def next_btn_click(self):

        """ Player event: When the NEXT button is clicked."""

        if not self.has_four_cards():
            self.show_message('Pull a card before clicking NEXT.')
            return

        event = NextTurn(self.player_id)
        self.client.send_game_event(event.to_bytes())

        self.action_done = False

    def show_message(self, text):
        self.message_text = text
        self.message_timer = time.time()

    def draw_message(self):
        if self.message_text is not None:
            if time.time() - self.message_timer < self.message_duration:
                arcade.draw_text(self.message_text,
                                 SCREEN_WIDTH / 2,
                                 SCREEN_HEIGHT / 2,
                                 arcade.color.YELLOW, 15,
                                 align="center", anchor_x='center', anchor_y='center')
            else:
                self.message_text = None
                self.message_timer = None
