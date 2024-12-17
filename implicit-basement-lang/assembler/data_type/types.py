from .data_type import DataType
from .number import (
    IntType, FloatType, VOID_TYPE, VOID_TYPE_NAME,
    INT_NAME_DICT, FLOAT_NAME_DICT
)
from .array import Array
from .pointer import PointerType
from .struct_decl import StructDecl


def get_data_type_name(data_type : DataType) -> str:
    match data_type:
        case IntType():
            if data_type is VOID_TYPE:
                name = VOID_TYPE_NAME
            else:
                name = INT_NAME_DICT[getattr(data_type, "issigned")][data_type]
        case FloatType():
            name = FLOAT_NAME_DICT[data_type]
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
