from dataclasses import dataclass
import typing


@dataclass
class ConnectionAttempt:
    user_id: int
    user_name: str


@dataclass
class User:
    IP: str
    PORT: int
    name: str
    user_id: int

    def __eq__(self, other):
        return self.user_id == other.user_id


@dataclass
class ConnectionState:
    confirmed_user: bool
    user_data: User


@dataclass
class GameState:
    user_count: int             # Number of players
    users: list                 # User() objects
    started: bool               # False when connecting, True when running
    current_turn: typing.Any    # User() object of the current player to move.
    player_cards: dict          # Dict of PlayerHand objects. Keys are player IDs.


@dataclass
class PlayerEvent:
    info: bool
    burn: bool
    place: bool
    pull: bool
    next_turn: bool = False

    def reset(self):
        self.info = False
        self.burn = False
        self.place = False
        self.pull = False
        self.next_turn = False
