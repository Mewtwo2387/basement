from .number import SIZE_TYPE


class PointerType(int):
    def __new__(cls, ref_type):
        obj = super().__new__(cls, SIZE_TYPE)
        setattr(obj, "ref_type", ref_type)
        setattr(obj, "size", SIZE_TYPE)
        return obj