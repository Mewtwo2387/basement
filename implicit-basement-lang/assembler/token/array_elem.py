from .delim import Delim


ARR_L_DELIM = "["
ARR_R_DELIM = "]"
ARR_MMB_DELIM = ","


class ArrayDelimLeft(Delim):
    char = ARR_L_DELIM

    def __str__(self) -> str:
        return f"Array{self.char}"


class ArrayDelimRight(Delim):
    char = ARR_R_DELIM

    def __str__(self) -> str:
        return f"{self.char}Array"


class ArraySubscriptDelimLeft(Delim):
    char = ARR_L_DELIM

    def __str__(self) -> str:
        return f"ArraySubscript{self.char}"


class ArraySubscriptDelimRight(Delim):
    char = ARR_R_DELIM

    def __str__(self) -> str:
        return f"{self.char}ArraySubscript"


class ArrayMemberDelim(Delim):
    char = ARR_MMB_DELIM