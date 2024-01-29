from .delim import Delim


ARR_L_DELIM = "["
ARR_R_DELIM = "]"
ARR_MMB_DELIM = ","


class ArrayDelimLeft(Delim):
    char = ARR_L_DELIM

class ArrayDelimRight(Delim):
    char = ARR_R_DELIM

class ArrayMemberDelim(Delim):
    char = ARR_MMB_DELIM