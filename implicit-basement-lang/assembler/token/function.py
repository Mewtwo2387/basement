from .token import ValueDict
from .token import Token
from ..data_type.types import DataType
from ..keywords import RETURN_KEYWORD

from collections import OrderedDict
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Function(Token):
    name:           str
    ret_type:       DataType
    arg_types:      OrderedDict[str, DataType]
    local_var_type: OrderedDict[str, DataType] = \
            field(init=False, default_factory=OrderedDict)

    def __post_init__(self) -> None:
        self.size = self.ret_type

    def update(
            self, *,
            address: Optional[int] = None,
            local_var: Optional[OrderedDict[str, DataType]] = None
        ) -> None:
        if address is not None:
            self.address = address

        if local_var is not None:
            if not isinstance(local_var, dict):
                raise TypeError("Invalid type for 'local_var'")

            for id, var_tok in local_var.items():
                if id in self.local_var_type:
                    raise ValueError(f"Local variable '{id}' "
                                     f"is already defined in {self.name}")
                self.local_var_type[id] = var_tok
                self.size += var_tok

    def get_value(self) -> ValueDict:
        return {
            "name": self.name,
            "size": self.size,
            "address": self.address
        }


@dataclass
class FunctionDeclaration(Function):
    pass


@dataclass
class FunctionCall(Token):
    func_name : str

    def __str__(self) -> str:
        return f"{self.__class__.__name__}(\"{self.func_name}\")"


class Return(Token):
    def __str__(self) -> str:
        return f"\"{RETURN_KEYWORD}\""