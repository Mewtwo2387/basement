from .token import ValueDict, Token
from ..data_type.types import DataType
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Variable(Token):
    name:      str
    data_type: DataType
    address:   int = field(init=False)

    def __post_init__(self):
        self.size = getattr(self.data_type, "size")
        self.value_token = Token()

    def update(self, address: Optional[int] = None) -> None:
        if address is not None:
            self.address = address
    
    def get_value(self) -> ValueDict:
        return {"size": self.size, "address": self.address}


@dataclass
class VariableInvoke(Token):
    name : str

    def __str__(self) -> str:
        return f"{self.__class__.__name__}(\"{self.name}\")"