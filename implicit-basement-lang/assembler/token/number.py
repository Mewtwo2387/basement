from .token import Token, ValueDict
from ..data_type.number import IntType, FloatType
from ..data_type.types import get_data_type_name
from dataclasses import dataclass


@dataclass
class Integer(Token):
    value: int
    type:  IntType

    def get_value(self) -> ValueDict:
        return {"value": self.value, "type": self.type}
    
    def __str__(self) -> str:
        return (f"{self.__class__.__name__}({self.value}, "
                f"type={get_data_type_name(self.type)})")


@dataclass
class Float(Token):
    value: float
    type:  FloatType

    def get_value(self) -> ValueDict:
        return {"value": self.value, "type": self.type}

    def __str__(self) -> str:
        return (f"{self.__class__.__name__}({self.value}, "
                f"type={get_data_type_name(self.type)})")


NumberToken = Integer | Float