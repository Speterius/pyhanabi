from dataclasses import dataclass
import pickle


@dataclass
class ConnectionAttempt:
    user_name: str

    def type(self):
        return type(self)


@dataclass
class ConnectionConfirmed:
    confirmed: bool
    user_name: str
    player_id: int

    def to_pickle(self):
        return pickle.dumps(self)


@dataclass
class Player:
    IP: str
    PORT: int
    name: str
    user_id: int

    def __eq__(self, other):
        return self.user_id == other.user_id


@dataclass
class GameStateUpdate:
    started: bool
    players: dict
    player_hands: dict
    table_stash: dict
    discard_pile: list
    info_points: int
    life_points: int
    current_player: int

    def to_pickle(self):
        return pickle.dumps(self)

    def type(self):
        return type(self)

