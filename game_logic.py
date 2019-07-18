import pickle
import pprint
from dataclasses import dataclass
import random
from data_packets import GameStateUpdate


@dataclass
class Card:
    color: str
    number: int

    def get_card_data(self):
        return self.color, self.number


class Deck:
    def __init__(self):
        # Store Card() objects:
        self.cards = []

        # Structure of the deck:
        self.deck_dict = {1: 3,     # Number of ones
                          2: 2,     # Number of twos
                          3: 2,     # Number of threes
                          4: 2,     # Number of fours
                          5: 1}     # Number of fives

        # Available colors:
        self.colors = ['blue', 'red', 'green', 'yellow', 'white']

        # Generate Cards:
        for col in self.colors:                             # For a given color col
            for num in self.deck_dict.keys():               # For a given number num
                for _ in range(self.deck_dict[num]):        # Generate a card a number of times given by deck_dict
                    c = Card(col, num)
                    self.cards.append(c)

        # Printable form of cards list:
        self.deck_state = {}
        self.update_state()

    def update_state(self):
        for col in self.colors:
            self.deck_state[col] = self.get_cards_with_color(col)

    def pull_card(self):
        card = random.choice(self.cards)
        self.cards.remove(card)
        self.update_state()
        return card

    def __str__(self):
        return str(self.deck_state)

    # Returns all cards within the deck with color: col
    def get_cards_with_color(self, col):
        cards_with_color = []
        for card in self.cards:
            if card.color == col:
                cards_with_color.append(card)
        return cards_with_color


@dataclass
class Event:
    player: int

    def to_json(self):
        pass

    def to_packet(self):
        return pickle.dumps(self)


class InfoUsed(Event):
    pass


class CardBurned(Event):
    card: Card
    card_position: int


class CardPlaced(Event):
    card: Card
    card_position: int


class CardPull(Event):
    pass


class NextTurn(Event):
    pass


class GameState:
    def __init__(self, n_players):
        self.n_players = n_players

        self.deck = Deck()                                          # Cards still in the deck
        self.table_stash = dict.fromkeys(self.deck.colors, [])      # Cards placed on the table
        self.discard_pile = []                                      # Cards burned/discarded

        assert 2 <= n_players <= 4
        self.player_hands = dict.fromkeys(range(n_players), dict)   # Cards in player's hands

        for player in self.player_hands.keys():

            hand = {0: self.deck.pull_card(),
                    1: self.deck.pull_card(),
                    2: self.deck.pull_card(),
                    3: self.deck.pull_card()}

            self.player_hands[player] = hand

        self.current_player = 0
        self.action_done = False   # To check if next player button is allowed.

        self.info_points: int = 9
        self.life_points: int = 3

        self.started = False
        self.lost = False

        self.send_GS = None

    def to_packet(self, players):

        game_state_update = GameStateUpdate(started=self.started,
                                            players=players,
                                            player_hands=self.player_hands,
                                            table_stash=self.table_stash,
                                            discard_pile=self.discard_pile,
                                            info_points=self.info_points,
                                            life_points=self.life_points,
                                            current_player=self.current_player)

        return game_state_update.to_pickle()

    def lose_life_point(self):
        self.life_points -= 1

        if self.life_points == 0:
            self.lost = True

    def lose_info_point(self):
        self.info_points = max(self.info_points-1, 0)

    def add_info_point(self):
        self.info_points = min(self.info_points+1, 9)

    def print_deck(self):
        pprint.pprint(self.deck.deck_state)

    def __str__(self):
        s = "GameState: \n"
        s += f"    Life Points: {self.life_points}\n"
        s += f"    Info Points: {self.info_points}\n"
        s += f"    Current Player: {self.current_player}\n"

    def update(self, event):
        # Possible events: InfoUsed, CardBurned, CardPlaced, CardPull, NextTurn
        # Returns True on successful update to GameState.       -> denotes 'changed = True' bool
        # Returns False, when event request is not possible.    -> denotes 'changed = False' bool, no need to broadcast

        # Only accept events from the current player:
        if self.current_player != event.player:
            print('Not this players turn.')
            return False

        # When a player gives someone info:
        if type(event) is InfoUsed and not self.action_done:

            # If they enoughh points left:
            if self.info_points > 0:

                # Lose a point of info:
                self.lose_info_point()

                # Did a valid action this turn:
                self.action_done = True

                # Successful Update of GameState:
                print('Info point taken')
                return True
            else:
                print('No info left to do that.')
                return False

        # When a player burns a card:
        elif type(event) is CardBurned and not self.action_done:

            # Get an info point back:
            self.add_info_point()

            # Remove the card from the player's hand:
            self.player_hands[event.player][event.card_position] = None

            # Add that card to the discard pile:
            self.discard_pile.append(event.card)

            # Did a valid action this turn:
            self.action_done = True

            # Successful Update of GameState:
            print('Card burned, info gained.')
            return True

        # When a player places a card on the table:
        elif type(event) is CardPlaced and not self.action_done:

            # Check whether for this color, this number is correct:
            # If yes: -> add card to table stash;
            if event.card.number == max(self.table_stash[event.card.color]) + 1:
                self.table_stash[event.card.color].append(event.card)
                print('Correct card placement.')

            # If not: -> add card to discard pile and lose a life.
            else:
                print('Wrong card placement, life lost')
                self.discard_pile.append(event.card)
                self.lose_life_point()

            # Take the card out of the player's hand:
            self.player_hands[event.player][event.card_position] = None

            # Did a valid action this turn:
            self.action_done = True

            # Successful Update of GameState:
            return True

        # When a player pulls a card:
        elif type(event) is CardPull:

            # Search for the empty slot in a player's hand and pull a card into it:
            for card_position in self.player_hands[event.player].keys():
                if self.player_hands[event.player][card_position] is None:
                    self.player_hands[event.player][card_position] = self.deck.pull_card()

                    # Successful Card Pull and update to GameState:
                    print('New card pulled.')
                    return True

            # The search for the card did not return, so the player has all cards already:
            print('Player has all cards. Cannot pull card.')
            return False

        # When a player clicks next turn:
        elif type(event) is NextTurn:

            # Next Turn is only possible if an action has already been done and the player has all cards:

            # Check if the player has all cards:
            has_all_cards = None not in self.player_hands[event.player].values()

            if self.action_done and has_all_cards:

                # Reset action done.
                self.action_done = False

                # rotate through 0->1->...->(n_players - 1)->0
                self.current_player = (self.current_player + 1) % self.n_players
                print('Switched to Next Player')
                return True
            else:
                print('Current Player has not done any of: [Place, Info, Burn]')
                return False
