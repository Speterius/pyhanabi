import pprint
from dataclasses import dataclass, field
import random


@dataclass
class PlayerEvent:
    player_ID: int
    info_used: bool


@dataclass
class Card:
    _color: str
    _number: int
    _ID: int

    def get_card_data(self):
        return self._color, self._number

    def get_color(self):
        return self._color

    def get_number(self):
        return self._number


class Deck:
    def __init__(self):
        # Store Card() objects:
        self.cards = []

        # Structure of the deck:
        self.deck_dict = {1: 3,
                          2: 2,
                          3: 2,
                          4: 2,
                          5: 1}

        # Available colors:
        self.colors = ['blue', 'red', 'green', 'yellow', 'white']

        # Generate Cards:
        i = 0
        for col in self.colors:
            for num in self.deck_dict.keys():
                for _ in range(self.deck_dict[num]):
                    self.cards.append(Card(col, num, i))

        # Printable form of cards list:
        self.deck_state = {}

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

    def get_cards_with_color(self, col):
        cards_with_color = []
        for card in self.cards:
            if card.get_color() == col:
                cards_with_color.append(card)
        return cards_with_color


class PlayerHand:
    def __init__(self, deck, ID):
        self.ID = ID
        self.card_1 = deck.pull_card()
        self.card_2 = deck.pull_card()
        self.card_3 = deck.pull_card()
        self.card_4 = deck.pull_card()

        self.cards = [self.card_1, self.card_2, self.card_3, self.card_4]

        self.updated: float = 0

        self.hand = {1: self.card_1,
                     2: self.card_2,
                     3: self.card_3,
                     4: self.card_4}

    def burn_card(self, card_index):
        self.cards.remove(self.cards[card_index])
        print('deleting: '+str(self.hand[card_index]))
        del self.hand[card_index]

    def print_hand(self):
        pprint.pprint(self.hand)


class GameState:
    def __init__(self, n_players):
        self.deck = Deck()      # Cards still in the deck
        self.placed = []        # Cards placed on the table
        self.player_hands = []  # Cards in Players Hands

        assert 2 <= n_players <= 4

        for i in range(n_players):
            self.player_hands.append(PlayerHand(self.deck, ID=i))

        self._info_points_left: int = 9
        self._life_points_left: int = 3

        self.started = False
        self.lost = False

    def set_life_points(self, val):
        self._life_points_left = val

    def get_life_points(self):
        return self._life_points_left

    def lose_life_point(self):
        self._life_points_left -= 1
        if self._life_points_left == 0:
            self.lost = True

    def set_info_points(self, val):
        self._info_points_left = val

    def get_info_points(self):
        return self._info_points_left

    def lose_info(self):
        self._info_points_left -= 1

    def add_info(self):
        self._info_points_left += 1

    def __str__(self):
        s = 'Player Hand  1:\n'
        for c in self.player_hands[0].cards:
            s += f'    {c.get_card_data()} \n'
        return s

    def print_deck(self):
        pprint.pprint(self.deck.deck_state)

    def print_player_hands(self):
        for p in self.player_hands:
            p.print_hand()
