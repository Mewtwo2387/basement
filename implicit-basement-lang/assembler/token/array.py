from .token import ValueDict
from .token import Token
from data_type.typing import DataType
from dataclasses import dataclass


@dataclass
class Array(Token):
    type:  DataType
    value: list[Token]

    def __post_init__(self):
       self.size = self.type * len(self.value)
    
    def update(self, *, new_val: Token) -> None:
        self.value.append(new_val)
        self.size += self.type

    def get_value(self) -> ValueDict:
        return {
            "size" : self.size,
            "type" : self.type,
            "value" : self.value.copy()
        }
