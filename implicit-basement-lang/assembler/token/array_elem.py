from .delim import Delim


ARR_L_DELIM = "["
ARR_R_DELIM = "]"

class ArraySubscriptDelimLeft(Delim):
    char = ARR_L_DELIM

    def __str__(self) -> str:
        return f"ArraySubscript{self.char}"


class ArraySubscriptDelimRight(Delim):
    char = ARR_R_DELIM

    def __str__(self) -> str:
        return f"{self.char}ArraySubscript"
