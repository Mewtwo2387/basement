from .token import Token
from ..keywords import RETURN_KEYWORD


class Return(Token):
    def __str__(self) -> str:
        return RETURN_KEYWORD