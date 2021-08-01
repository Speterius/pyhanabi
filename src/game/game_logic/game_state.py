from common.packets import GameStateUpdate, CardPlaced, CardBurned, CardPull, InfoUsed, NextTurn, Event
from .deck import Deck, Card
from typing import List, TypedDict
from dataclasses import dataclass


@dataclass
class Player:
    number: int
    id: int
    name: str


@dataclass
class PlayerHand:
    player: Player
    cards: List[Card]


class GameState:
    def __init__(self, n_players: int):
        if not (2 <= n_players <= 4):
            raise ValueError("Number of players must be 2, 3 or 4.")

        self.n_players: int = n_players

        # Cards still in the deck
        self.deck: Deck = Deck()

        # Cards placed on the table
        self.table_stash: TypedDict[str, List[Card]] = dict.fromkeys(self.deck.colors, [])

        # Cards burned / discarded
        self.discard_pile: List[Card] = []

        # Cards in the hands of players
        self.player_hands: TypedDict[int, TypedDict[int, Card]] = {}

        for player in self.player_hands.keys():

            hand = {0: self.deck.pull_card(),
                    1: self.deck.pull_card(),
                    2: self.deck.pull_card(),
                    3: self.deck.pull_card()}

            self.player_hands[player] = hand

        self.current_player_index: int = 0                          # Will only accept game state updates from this id.
        self.action_done: bool = False                               # To check if next player button is allowed.

        self.info_points: int = 9
        self.life_points: int = 3

        self.started: bool = False
        self.lost: bool = False

    def to_bytes(self, players):

        """ This method converts the necessary game state variables into a DataPacket object from data_packets."""

        game_state_update = GameStateUpdate(started=self.started,
                                            players=players,
                                            player_hands=self.player_hands,
                                            table_stash=self.table_stash,
                                            discard_pile=self.discard_pile,
                                            info_points=self.info_points,
                                            life_points=self.life_points,
                                            current_player=self.current_player_index)

        return game_state_update.to_bytes()

    def lose_life_point(self):
        self.life_points -= 1

        if self.life_points == 0:
            self.lost = True

    def lose_info_point(self):
        # Cannot use info points when 0
        self.info_points = max(self.info_points-1, 0)

    def add_info_point(self):
        # Cannot get more info points than 9
        self.info_points = min(self.info_points+1, 9)

    def __str__(self):
        s = "GameState: \n"
        s += f"    Life Points: {self.life_points}\n"
        s += f"    Info Points: {self.info_points}\n"
        s += f"    Current Player: {self.current_player_index}\n"

    def update(self, event: Event) -> bool:

        """
        Possible events: InfoUsed, CardBurned, CardPlaced, CardPull, NextTurn

        Returns True on successful update to GameState.       -> denotes 'changed = True' bool
        Returns False, when event request is not possible.    -> denotes 'changed = False' bool, no need to broadcast
        """

        # Only accept events from the current player:
        if self.current_player_index != event.player:
            print(f"Not this player's turn.")
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
                self.current_player_index = (self.current_player_index + 1) % self.n_players
                print('Switched to Next Player')
                return True
            else:
                print('Current Player has not done any of: [Place, Info, Burn]')
                return False
