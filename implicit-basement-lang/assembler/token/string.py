from .token import Token
from ..data_type.number import CHAR_TYPE
from dataclasses import dataclass


@dataclass
class String(Token):
    value: str

    def __post_init__(self):
        self.size = CHAR_TYPE * len(self.value)