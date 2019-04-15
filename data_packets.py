from dataclasses import dataclass


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
    users: list
    started: bool


@dataclass
class PlayerEvent:
    info: bool
    burn: bool
    place: bool
    pull: bool
