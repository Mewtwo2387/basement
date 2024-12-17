from .delim import Delim


STRUCT_KEYWORD = "struct"
STRUCT_L_DELIM = "{"
STRUCT_R_DELIM = "}"
STRUCT_MMB_DELIM = ","


class StructDelimLeft(Delim):
    char = STRUCT_L_DELIM

    def __str__(self) -> str:
        return f'StructInit"{self.char}"'

class StructDelimRight(Delim):
    char = STRUCT_R_DELIM

    def __str__(self) -> str:
        return f'"{self.char}"StructInit'

class StructMemberDelim(Delim):
    char = STRUCT_MMB_DELIM

    def __str__(self) -> str:
        return f'StructInit"{self.char}"'