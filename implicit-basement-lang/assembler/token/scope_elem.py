from .delim import Delim
from enum import Enum


SCOPE_START_KEYWORD = ":"
SCOPE_END_KEYWORD = "end"


class ScopeStart(Delim):
    def __str__(self) -> str:
        return f"{self.__class__.__name__}"


class ScopeEnd(Delim):
    def __str__(self) -> str:
        return f"{self.__class__.__name__}"


class ScopeType(Enum):
    GENERIC     = 0
    FUNCTION    = 1
    BLOCK       = 2
    CONDITIONAL = 3
    LOOP        = 4