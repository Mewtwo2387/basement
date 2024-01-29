from .token import Token


IF_KEYWORD = "if"
ELSE_KEYWORD = "else"
END_IF_KEYWORD = "if"

LOOP_KEYWORD = "loop"
END_LOOP_KEYWORD = "loop"
LOOP_CONT_KEYWORD = "continue"
LOOP_BREAK_KEYWORD = "break"


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