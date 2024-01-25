from .token import Token, ValueDict
from ..data_type.number import IntType, FloatType
from dataclasses import dataclass


@dataclass
class Integer(Token):
    value: int
    type:  IntType

    def get_value(self) -> ValueDict:
        return {"value": self.value, "type": self.type}
    
    def __str__(self) -> str:
        return f"{self.__class__.__name__}({self.value}, size={self.type})"


@dataclass
class Float(Token):
    value: float
    type:  FloatType

    def get_value(self) -> ValueDict:
        return {"value": self.value, "type": self.type}

    def __str__(self) -> str:
        return f"{self.__class__.__name__}({self.value}, size={self.type})"


NumberToken = Integer | Float