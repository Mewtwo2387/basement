from .token import Token


COMMA_CHAR = ","
EOL = ";"

EXPR_GROUP_L_DELIM = "("
EXPR_GROUP_R_DELIM = ")"


class Delim(Token):
    char = None

    def __str__(self) -> str:
        return f"\"{self.char}\""


class Comma(Delim):
    char = COMMA_CHAR


class EndOfLine(Delim):
    def __str__(self) -> str:
        return "EOL"


class ExprGroupDelimLeft(Delim):
    char = EXPR_GROUP_L_DELIM

    def __str__(self) -> str:
        return f"Expr{self.char}"

class ExprGroupDelimRight(Delim):
    char = EXPR_GROUP_R_DELIM

    def __str__(self) -> str:
        return f"{self.char}Expr"