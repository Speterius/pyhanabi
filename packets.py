import sys
import json
import pickle
from dataclasses import dataclass

''' This module defines the data packets to be sent between the server and the clients.
The base class DataPacket provides JSON serialization. The Dict2Obj can convert the sent
dictionaries back to their original DataPacket objects.'''


class Dict2Obj(object):
    def __init__(self, dictionary):
        for key, value in dictionary.items():
            setattr(self, key, value)


def get_events():
    return Event.__subclasses__()


def load(packet):
    d = json.loads(packet.decode('utf-8'))
    d['__class__'] = getattr(sys.modules[__name__], d['__class__'])

    new_instance = Dict2Obj(d)

    return new_instance


class DataPacket:
    def to_pickle(self):
        return pickle.dumps(self)

    def to_dict(self):

        #  Populate the dictionary with object meta data
        obj_dict = {
            '__class__': self.__class__.__name__
        }

        #  Populate the dictionary with object properties
        obj_dict.update(self.__dict__)

        return obj_dict

    def to_json(self):
        # d = self.to_dict()
        return json.dumps(self.to_dict())

    def to_bytes(self):
        return bytes(self.to_json(), 'utf-8')


@dataclass
class ConnectionAttempt(DataPacket):
    user_name: str


@dataclass
class ConnectionConfirmed(DataPacket):
    confirmed: bool
    user_name: str
    player_id: int


@dataclass
class Card:
    color: str
    number: int

    def get_card_data(self):
        return self.color, self.number


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


@dataclass
class Event(DataPacket):
    player: int


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
    card: Card
    card_position: int


@dataclass
class CardPlaced(Event):
    card: Card
    card_position: int
