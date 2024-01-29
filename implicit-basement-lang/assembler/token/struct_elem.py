from .delim import Delim


STRUCT_KEYWORD = "struct"
STRUCT_L_DELIM = "{"
STRUCT_R_DELIM = "}"
STRUCT_MMB_DELIM = ","


class StructDelimLeft(Delim):
    char = STRUCT_L_DELIM

class StructDelimRight(Delim):
    char = STRUCT_R_DELIM

class StructMemberDelim(Delim):
    char = STRUCT_MMB_DELIM