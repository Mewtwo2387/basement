from .number import SIZE_TYPE
from .data_type import DataType


POINTER_CHAR = "*"


class PointerType(DataType):
    ref_type: DataType

    def __new__(cls, ref_type):
        obj = super().__new__(cls, SIZE_TYPE)
        setattr(obj, "ref_type", ref_type)
        setattr(obj, "size", SIZE_TYPE)
        return obj