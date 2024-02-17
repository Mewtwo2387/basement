from .token import ValueDict
from .token import Token
from .variable import Variable
from ..data_type.types import DataType, get_data_type_name

from dataclasses import dataclass, field
from typing import Optional


FUNCTION_KEYWORD = "function"
FUNC_ARG_L_BRACKET = "("
FUNC_ARG_R_BRACKET = ")"
FUNC_ARG_DELIM = ","
FUNC_RET_SYMBOL = "=>"

RETURN_KEYWORD = "return"


@dataclass
class Function(Token):
    name:           str
    ret_type:       DataType
    arg_list:       list[Variable]
    local_var_dict: dict[str, Variable] = field(init=False)

    def __post_init__(self) -> None:
        self.size = self.ret_type

    def update(
            self, *,
            address:   Optional[int] = None,
            local_var: Optional[list[Variable]] = None
        ) -> None:
        if address is not None:
            self.address = address

        if local_var is not None:
            if not isinstance(local_var, list):
                raise TypeError("Invalid type for 'local_var'")

            for var_token in local_var:
                if var_token.name in self.local_var_dict:
                    raise ValueError(f"Local variable '{id}' "
                                     f"is already defined in {self.name}")
                self.local_var_dict[var_token.name] = var_token
                self.size += var_token.data_type

    def get_value(self) -> ValueDict:
        return {
            "name": self.name,
            "size": self.size,
            "address": self.address
        }
    
    def __str__(self) -> str:
        ret_type_name = get_data_type_name(self.ret_type)
        arg_type_names = [get_data_type_name(arg.data_type) + f" {arg.name}"
                          for arg in self.arg_list]
        return f"{ret_type_name} {self.name}({', '.join(arg_type_names)})"


@dataclass
class FunctionDeclaration(Function):
    pass


@dataclass
class FunctionCall(Token):
    name : str

    def __str__(self) -> str:
        return f"{self.__class__.__name__}(\"{self.name}\")"


class ArgBracketLeft(Token):
    def __str__(self) -> str:
        return f"Func("


class ArgBracketRight(Token):
    def __str__(self) -> str:
        return f")Func"


class ArgDelim(Token):
    def __str__(self) -> str:
        return f'Func","'


class Return(Token):
    def __str__(self) -> str:
        return f"\"{RETURN_KEYWORD}\""