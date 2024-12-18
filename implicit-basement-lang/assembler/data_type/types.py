from .data_type import DataType
from .number import IntType, FloatType
from .array import Array
from .pointer import PointerType
from .struct_decl import StructDecl


def get_data_type_name(data_type : DataType) -> str:
    match data_type:
        case IntType() | FloatType():
            name = data_type.name
        case StructDecl():
            name = f"struct {getattr(data_type, 'name')}"
        case PointerType():
            ref_type_name = get_data_type_name(getattr(data_type, "ref_type"))
            name = f"{ref_type_name}*"
        case Array():
            ref_type_name = get_data_type_name(getattr(data_type, "elem_type"))
            array_length = getattr(data_type, "length")
            name = f"{ref_type_name}[{array_length}]"
        case _:
            name = "???"
    return name
