from .token import Token
from ..keywords import (
    ARR_L_DELIM,
    ARR_R_DELIM,
    ARR_MMB_DELIM,
    STRUCT_L_DELIM,
    STRUCT_R_DELIM,
    STRUCT_MMB_DELIM,
    COMMA_CHAR,
    EXPR_GROUP_L_DELIM,
    EXPR_GROUP_R_DELIM
)


class Delim(Token):
    char = None

    def __str__(self) -> str:
        return f"\"{self.char}\""


class ArrayDelimLeft(Delim):
    char = ARR_L_DELIM

class ArrayDelimRight(Delim):
    char = ARR_R_DELIM

class ArrayMemberDelim(Delim):
    char = ARR_MMB_DELIM


class StructDelimLeft(Delim):
    char = STRUCT_L_DELIM

class StructDelimRight(Delim):
    char = STRUCT_R_DELIM

class StructMemberDelim(Delim):
    char = STRUCT_MMB_DELIM


class Comma(Delim):
    char = COMMA_CHAR


class ScopeStart(Delim):
    def __str__(self) -> str:
        return f"{self.__class__.__name__}"

class ScopeEnd(Delim):
    def __str__(self) -> str:
        return f"{self.__class__.__name__}"

class EndOfLine(Delim):
    def __str__(self) -> str:
        return "EOL"


class ExprGroupDelimLeft(Delim):
    char = EXPR_GROUP_L_DELIM

class ExprGroupDelimRight(Delim):
    char = EXPR_GROUP_R_DELIM