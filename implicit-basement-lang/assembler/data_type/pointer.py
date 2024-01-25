from .number import U_INT64

PTR_SIZE_TYPE = U_INT64

class PointerType(int):
    def __new__(cls, ref_type):
        obj = super().__new__(cls, PTR_SIZE_TYPE)
        setattr(obj, "ref_type", ref_type)
        setattr(obj, "size", PTR_SIZE_TYPE)
        return obj