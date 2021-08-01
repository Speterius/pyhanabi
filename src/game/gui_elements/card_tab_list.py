import typing
import arcade
from .card_tab import CardTab

# This is for type hinting to also accept CardTab instances and not just Sprites.
T = typing.TypeVar('T', bound=CardTab)


class CardTabList(arcade.SpriteList):
    def __init__(self):
        super().__init__()
        self.x = 0

    def __iter__(self) -> typing.Iterable[T]:
        return iter(self.sprite_list)
