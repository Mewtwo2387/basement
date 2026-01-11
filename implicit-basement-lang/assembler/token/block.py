from .scope_elem import ScopeStart, ScopeEnd
from .token import Token


BLOCK_KEYWORD = "block"
END_BLOCK_KEYWORD = "block"


class Block(Token):
    def __str__(self) -> str:
        return '"' + BLOCK_KEYWORD + '"'


class BlockScopeStart(ScopeStart):
    pass


class BlockScopeEnd(ScopeEnd):
    pass