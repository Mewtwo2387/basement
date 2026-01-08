from .data_type import DataType


class ArrayType(DataType):
    len: int
    mmb_type: DataType

    def __new__(cls, len: int, mmb_type: DataType):
        obj = super().__new__(cls, mmb_type.size * len)

        setattr(obj, "size", obj)
        setattr(obj, "name", f"{mmb_type.name}[{len}]")
        setattr(obj, "len", len)
        setattr(obj, "mmb_type", mmb_type)

        return obj