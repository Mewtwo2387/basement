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
        return f"\"{self.keyword}\""


class If(BranchControl):
    keyword = IF_KEYWORD


class Else(BranchControl):
    keyword = ELSE_KEYWORD


class Loop(BranchControl):
    keyword = LOOP_KEYWORD


class LoopContinue(BranchControl):
    keyword = LOOP_CONT_KEYWORD

class LoopBreak(BranchControl):
    keyword = LOOP_BREAK_KEYWORD