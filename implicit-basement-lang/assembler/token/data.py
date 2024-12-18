from dataclasses import dataclass
from typing import Any

from .token import Token, ValueDict
from ..data_type.data_type import DataType
from ..data_type.types import get_data_type_name


@dataclass
class Data(Token):
    value: Any
    type:  DataType

    def get_value(self) -> ValueDict:
        return {"value": self.value, "type": self.type}

    def __str__(self) -> str:
        return (f"{self.__class__.__name__}({self.value}, "
                f"type={get_data_type_name(self.type)})")