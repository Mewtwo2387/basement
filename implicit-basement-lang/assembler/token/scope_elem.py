from .delim import Delim


SCOPE_START = ":"
SCOPE_START_ALT = "{"
SCOPE_END = "end"
SCOPE_END_ALT = "}"

SCOPE_BLOCK_KEYWORD = "block"
END_SCOPE_BLOCK_KEYWORD = "block"


class ScopeStart(Delim):
    def __str__(self) -> str:
        return f"{self.__class__.__name__}"

class ScopeEnd(Delim):
    def __str__(self) -> str:
        return f"{self.__class__.__name__}"