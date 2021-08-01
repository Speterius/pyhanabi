from dataclasses import dataclass
from game.game_logic.deck import Card
from .data_packet import DataPacket
from typing import Optional


@dataclass
class ConnectionAttempt(DataPacket):
    user_name: str


@dataclass
class ConnectionConfirmed(DataPacket):
    confirmed: bool
    user_name: str
    player_id: int


@dataclass
class Event(DataPacket):
    player: int
    card: Optional[Card] = None
    card_position: Optional[int] = None


@dataclass
class InfoUsed(Event):
    pass


@dataclass
class CardPull(Event):
    pass


@dataclass
class NextTurn(Event):
    pass


@dataclass
class CardBurned(Event):
    pass


@dataclass
class CardPlaced(Event):
    pass


@dataclass
class GameStateUpdate(DataPacket):
    started: bool
    players: dict

    player_hands: dict
    table_stash: dict
    discard_pile: list

    info_points: int
    life_points: int
    current_player: int

    def cards_to_dicts(self):

        self.player_hands = {i: {ix: card.__dict__ for ix, card in hand.items()}
                             for i, hand in self.player_hands.items()}

        self.table_stash = {color: [card.__dict__ for card in card_lst]
                            for color, card_lst in self.table_stash.items()}

        self.discard_pile = [card.__dict__ for card in self.discard_pile]

    def keys_to_ints(self):

        self.players = {int(player_id): name for player_id, name in self.players.items()}

        self.player_hands = {int(idx): {int(ix): card for ix, card in hand.items()}
                             for idx, hand in self.player_hands.items()}

    def to_bytes(self):

        # Convert Cards to dicts
        self.cards_to_dicts()
        return super().to_bytes()
