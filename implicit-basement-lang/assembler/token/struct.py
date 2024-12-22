from dataclasses import dataclass, field
from itertools import zip_longest

from .token import ValueDict
from .data import Data
from .number import Integer, Float
from .pointer import Pointer
from .delim import Delim

from ..data_type.number import IntType, FloatType
from ..data_type.pointer import PointerType
from ..data_type.struct_decl import StructDecl


STRUCT_KEYWORD = "struct"
STRUCT_L_DELIM = "{"
STRUCT_R_DELIM = "}"
STRUCT_MMB_DELIM = ","


class StructDelimLeft(Delim):
    char = STRUCT_L_DELIM

    def __str__(self) -> str:
        return f'StructInit"{self.char}"'


class StructDelimRight(Delim):
    char = STRUCT_R_DELIM

    def __str__(self) -> str:
        return f'"{self.char}"StructInit'


class StructMemberDelim(Delim):
    char = STRUCT_MMB_DELIM

    def __str__(self) -> str:
        return f'StructInit"{self.char}"'