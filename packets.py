import sys
import json
import pickle
from dataclasses import dataclass
from game_logic import Card

''' This module defines the data packets to be sent between the server and the clients.
The base class DataPacket provides JSON serialization. The module variables can be used
to match packet types with the __class__ Key.'''

# Globals for type matching:
# CON_ATTEMPT = 'ConnectionAttempt'
# CON_CONFIRM = 'ConnectionConfirmed'
# GS_UPDATE = 'GameStateUpdate'
#
# INFO_USED = 'InfoUsed'
# CARD_PULL = 'CardPull'
# CARD_PLACE = 'CardPlaced'
# CARD_BURN = 'CardBurned'
# NEXT_TURN = 'NextTurn'
#
# PLAYEREVENTS = [INFO_USED, CARD_PULL, CARD_BURN, CARD_PLACE, NEXT_TURN]


class Dict2Obj(object):
    def __init__(self, dictionary):
        for key, value in dictionary.items():
            setattr(self, key, value)


def get_events():
    return []


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
class GameStateUpdate(DataPacket):
    started: bool
    players: dict
    player_hands: dict
    table_stash: dict
    discard_pile: list
    info_points: int
    life_points: int
    current_player: int


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
