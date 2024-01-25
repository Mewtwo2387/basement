from .number import IntType, FloatType
from .pointer import PointerType
from collections import OrderedDict
from typing import Union


_DataType = IntType | FloatType | PointerType

class Struct(int):
    def __new__(cls, name: str,
                member_types: OrderedDict[str, Union[_DataType, "Struct"]]):
        size_tuple = tuple(T for T in member_types.values())
        total_size = sum(size_tuple)
        obj = super().__new__(cls, total_size)
        setattr(obj, "size", obj)
        setattr(obj, "name", name)
        setattr(obj, "fields", member_types.copy())
        return obj

    def get_member_sizes(self) -> tuple[Union[_DataType, "Struct"], ...]:
        field_dict: OrderedDict[str, Union[_DataType, "Struct"]] = \
            getattr(self, "fields")
        return tuple(field_dict.values())