from .delim import Delim


SCOPE_START_KEYWORD = ":"
SCOPE_END_KEYWORD = "end"


class ScopeStart(Delim):
    def __str__(self) -> str:
        return f"{self.__class__.__name__}"

class ScopeEnd(Delim):
    def __str__(self) -> str:
        return f"{self.__class__.__name__}"