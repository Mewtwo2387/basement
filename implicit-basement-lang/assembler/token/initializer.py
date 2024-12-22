from .delim import Delim


INITIALIZER_L_DELIM = "{"
INITIALIZER_R_DELIM = "}"
INITIALIZER_MMB_DELIM = ","


class InitDelimLeft(Delim):
    char = INITIALIZER_L_DELIM

    def __str__(self) -> str:
        return f'Init"{self.char}"'


class InitDelimRight(Delim):
    char = INITIALIZER_R_DELIM

    def __str__(self) -> str:
        return f'"{self.char}"Init'


class InitMemberDelim(Delim):
    char = INITIALIZER_MMB_DELIM

    def __str__(self) -> str:
        return f'Init"{self.char}"'