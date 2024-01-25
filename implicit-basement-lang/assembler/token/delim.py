from .token import Token
from ..keywords import (
    ARR_L_DELIM,
    ARR_R_DELIM,
    ARR_MMB_DELIM,
    STRUCT_L_DELIM,
    STRUCT_R_DELIM,
    STRUCT_MMB_DELIM,
    COMMA_CHAR,
    SCOPE_START,
    SCOPE_END,
    SCOPE_START_ALT,
    SCOPE_END_ALT,
    EOL
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
    char = f"{SCOPE_START}\" | \"{SCOPE_START_ALT}"

class ScopeEnd(Delim):
    char = f"{SCOPE_END}\" | \"{SCOPE_END_ALT}"

class EndOfLine(Delim):
    char = EOL