from .token import Token
from ..data_type.types import DataType
from dataclasses import dataclass, field


class AssignOp(Token):
    pass

class MemberAccessOp(Token):
    pass


@dataclass
class AbstractOperator(Token):
    op_str: str

@dataclass
class LeftUnaryOp(AbstractOperator):
    pass

@dataclass
class TypeCastOp(AbstractOperator):
    op_str: str = field(init=False, default="typecast")

    def __init__(self, to_type: DataType):
        self.to_type = to_type


@dataclass
class RightUnaryOp(AbstractOperator):
    pass

@dataclass
class BinaryOp(AbstractOperator):
    pass