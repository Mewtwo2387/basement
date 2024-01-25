from .token import Token
from ..data_type.types import DataType
from ..keywords import ASSIGN_CHAR, STRUCT_MMB_ACCESS_OP
from dataclasses import dataclass, field


class AssignOp(Token):
    def __str__(self) -> str:
        return f"\"{ASSIGN_CHAR}\""

class MemberAccessOp(Token):
    def __str__(self) -> str:
        return f"\"{STRUCT_MMB_ACCESS_OP}\""


@dataclass
class AbstractOperator(Token):
    op_str: str

    def __str__(self) -> str:
        return f"{self.__class__.__name__}(\"{self.op_str}\")"

@dataclass
class LeftUnaryOp(AbstractOperator):
    pass

@dataclass
class TypeCastOp(AbstractOperator):
    op_str: str = field(init=False, default="typecast")

    def __init__(self, to_type: DataType):
        self.to_type = to_type

    def __str__(self) -> str:
        return f"{self.__class__.__name__}(\"{self.to_type}\")"


@dataclass
class RightUnaryOp(AbstractOperator):
    pass

@dataclass
class BinaryOp(AbstractOperator):
    pass