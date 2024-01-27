class Array(int):
    def __new__(cls, elem_type, length):
        obj = super().__new__(cls, elem_type * length)
        setattr(obj, "elem_type", elem_type)
        setattr(obj, "length", length)
        setattr(obj, "size", elem_type * length)
        return obj