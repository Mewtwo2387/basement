from .data_type import DataType

class Array(DataType):
    elem_type: DataType
    length:    int

    def __new__(cls, elem_type: DataType, length: int):
        obj = super().__new__(cls, elem_type * length)
        setattr(obj, "elem_type", elem_type)
        setattr(obj, "length", length)
        setattr(obj, "size", elem_type * length)
        return obj