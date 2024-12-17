from .number import SIZE_TYPE, IntType


POINTER_CHAR = "*"


class PointerType(int):
    size:     int
    ref_type: IntType

    def __new__(cls, ref_type):
        obj = super().__new__(cls, SIZE_TYPE)
        setattr(obj, "ref_type", ref_type)
        setattr(obj, "size", SIZE_TYPE)
        return obj