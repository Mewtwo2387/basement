from .token import Token


BLOCK_KEYWORD = "block"
END_BLOCK_KEYWORD = "block"


class Block(Token):
    def __str__(self) -> str:
        return '"' + BLOCK_KEYWORD + '"'