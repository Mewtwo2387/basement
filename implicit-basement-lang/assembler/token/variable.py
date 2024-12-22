from .token import ValueDict, Token
from ..data_type.types import DataType, get_data_type_name
from dataclasses import dataclass, field
from typing import Optional

from ..error import TokenizeError


VAR_ATTR_STR_LIST = ("const", )


@dataclass
class Variable(Token):
    name:      str
    data_type: DataType
    attrib:    str | None = field(default=None)
    address:   int        = field(init=False)

    def __post_init__(self):
        self.size = getattr(self.data_type, "size")
        self.value_token = Token()

    def update(self,
               attrib:  Optional[str] = None,
               address: Optional[int] = None) -> None:
        if attrib is not None:
            if attrib not in VAR_ATTR_STR_LIST:
                raise TokenizeError(f"\"{attrib}\" is not a valid variable"
                                    " attribute")
            self.attrib = attrib
        if address is not None:
            self.address = address

    def get_value(self) -> ValueDict:
        return {"size": self.size, "address": self.address}
    
    def __str__(self) -> str:
        return (f"{self.__class__.__name__}(\"{self.name}\", "
                f"type={get_data_type_name(self.data_type)})")


@dataclass
class VariableInvoke(Token):
    name : str

    def __str__(self) -> str:
        return f"{self.__class__.__name__}(\"{self.name}\")"