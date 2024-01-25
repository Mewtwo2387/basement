class IntType(int):
    def __new__(cls, size, issigned: bool):
        obj = super().__new__(cls, size)
        setattr(obj, "size", obj)
        setattr(obj, "issigned", issigned)
        return obj


class FloatType(int):
    def __new__(cls, size):
        obj = super().__new__(cls, size)
        setattr(obj, "size", obj)
        return obj


S_INT8  = IntType(1, True)
S_INT16 = IntType(2, True)
S_INT32 = IntType(4, True)
S_INT64 = IntType(8, True)
U_INT8  = IntType(1, False)
U_INT16 = IntType(2, False)
U_INT32 = IntType(4, False)
U_INT64 = IntType(8, False)

FLOAT32 = FloatType(4)
FLOAT64 = FloatType(8)

INT_TYPE_NAME = {
    "i8"  : S_INT8,
    "i16" : S_INT16,
    "i32" : S_INT32,
    "i64" : S_INT64,
    "u8"  : U_INT8,
    "u16" : U_INT16,
    "u32" : U_INT32,
    "u64" : U_INT64,
    "usize" : U_INT64
}

FLOAT_TYPE_NAME = {
    "f32" : FLOAT32,
    "f64" : FLOAT64
}

VOID_TYPE = IntType(0, True)
VOID_TYPE_NAME = "void"

DEFAULT_INT_TYPE = S_INT32
DEFAULT_FLOAT_TYPE = FLOAT32
CHAR_TYPE = S_INT8

NumberType = IntType | FloatType