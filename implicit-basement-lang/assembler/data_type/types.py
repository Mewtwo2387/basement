from .data_type import DataType
from .number import IntType, FloatType
from .struct_decl import StructDecl


def get_data_type_name(data_type : DataType) -> str:
    match data_type:
        case IntType() | FloatType():
            name = data_type.name
        case StructDecl():
            name = f"struct {getattr(data_type, 'name')}"
        case _:
            name = "???"
    return name
