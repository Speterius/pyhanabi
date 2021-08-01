import random
from dataclasses import dataclass
from typing import List


@dataclass
class Card:
    color: str
    number: int


class Deck:
    def __init__(self):

        # Store Card() objects:
        self.cards: List[Card] = []

        # Structure of the deck:
        self.deck_structure = {"n_ones":   3,
                               "n_twos":   2,
                               "n_threes": 2,
                               "n_fours":  2,
                               "n_fives":  1}

        # Available colors:
        self.colors = ['blue', 'red', 'green', 'yellow', 'white']

        # Generate Cards for each color and number based on the deck_structure:
        for card_color in self.colors:
            for card_number, (_, count) in enumerate(self.deck_structure.items()):
                self.cards += [Card(card_color, card_number) for _ in range(count)]

        # Printable form of cards list:

    def pull_card(self):
        card = random.choice(self.cards)
        self.cards.remove(card)
        return card

    def get_cards_by_color(self, color):
        return [c for c in self.cards if c.color == color]

    def get_cards_by_number(self, number):
        return [c for c in self.cards if c.number == number]

    @property
    def deck_state(self) -> dict:
        d = {}
        for color in self.colors:
            d[color] = self.get_cards_by_color(color)
        return d

    def __str__(self):
        return str(self.deck_state)
