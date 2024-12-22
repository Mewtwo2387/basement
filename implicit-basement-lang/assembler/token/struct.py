from dataclasses import dataclass, field
from itertools import zip_longest

from .token import ValueDict
from .data import Data
from .number import Integer, Float
from .pointer import Pointer
from .delim import Delim

from ..data_type.number import IntType, FloatType
from ..data_type.pointer import PointerType
from ..data_type.struct_decl import StructDecl


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

@dataclass
class Struct(Data):
    value: list[Data]
    type:  StructDecl | None = field(default=None)

    def __post_init__(self):
        if self.type is not None:
            self.__cast_field()
    
    def __cast_field(self):
        if self.type is None:
            raise TypeError("Cannot do internal type casting with no type")

        new_fields = []
        for inputfield, field_name in zip_longest(self.value, self.type.fields):
            if inputfield is None:
                raise TypeError(f"Missing field value for {field_name}")
            if field_name is None:
                raise TypeError( "Excess field value. "
                                f"Expected {len(self.type.fields)} value(s)")
            if not isinstance(inputfield, Data):
                raise TypeError("Incorrect internal field value type")
            if not isinstance(field_name, str):
                raise TypeError("Incorrect internal field name type")
            
            field_type = self.type.fields[field_name]

            if field_type == inputfield.type:
                new_fields.append(inputfield)
                continue

            match field_type:
                # Number types (ints and floats) can implicitly cast to
                # each other
                case IntType() | FloatType():
                    if not (   isinstance(inputfield.type, IntType)
                            or isinstance(inputfield.type, FloatType)):
                        raise TypeError(f"Cannot cast {inputfield.type.name} "
                                        f"to {field_type.name}")

                    if isinstance(field_type, IntType):
                        new_value = Integer(int(inputfield.value), field_type)
                    else:
                        new_value = Float(float(inputfield.value), field_type)
                
                case PointerType():
                    if not(   isinstance(inputfield.type, PointerType)
                           or isinstance(inputfield.type, IntType)):
                        raise TypeError(f"Cannot cast {inputfield.type.name} "
                                        f"to {field_type.name}")
                    new_value = Pointer(inputfield.value, field_type)

                case _:
                    raise TypeError(f"Type casting mismatch from "
                                    f"{inputfield.type.name} to "
                                    f"{field_type.name}")

            new_fields.append(new_value)


    def get_value(self) -> ValueDict:
        return {"value": tuple(self.value)}
    
    def update(self, struct_type: StructDecl) -> None:
        self.type = struct_type
        self.__cast_field()