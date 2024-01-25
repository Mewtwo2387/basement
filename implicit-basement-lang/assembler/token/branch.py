from .token import Token
from ..keywords import (
    IF_KEYWORD,
    ELSE_KEYWORD,
    LOOP_KEYWORD,
    LOOP_CONT_KEYWORD,
    LOOP_BREAK_KEYWORD
)

class BranchControl(Token):
    keyword = None

    def __str__(self) -> str:
        return f"{self.keyword}"


class If(Token):
    keyword = IF_KEYWORD


class Else(Token):
    keyword = ELSE_KEYWORD


class Loop(Token):
    keyword = LOOP_KEYWORD


class LoopContinue(Token):
    keyword = LOOP_CONT_KEYWORD

class LoopBreak(Token):
    keyword = LOOP_BREAK_KEYWORD