from .data_type import DataType


class IntType(DataType):
    issigned: bool

    def __new__(cls, size, issigned: bool):
        obj = super().__new__(cls, size)
        setattr(obj, "size", obj)
        setattr(obj, "issigned", issigned)
        return obj


class FloatType(DataType):
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

INT_STR_TO_TYPE_DICT = {
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

# NOTE: The keys for this dict pertains to the value of "issigned" attribute of
#       IntType objects.
INT_NAME_DICT = {
    True: {
        S_INT8  : "int8",
        S_INT16 : "int16",
        S_INT32 : "int32",
        S_INT64 : "int64",
    },
    False : {
        U_INT8  : "uint8",
        U_INT16 : "uint16",
        U_INT32 : "uint32",
        U_INT64 : "uint64",
    }
}

FLOAT_STR_TO_TYPE_DICT = {
    "f32" : FLOAT32,
    "f64" : FLOAT64
}

FLOAT_NAME_DICT = {
    FLOAT32 : "f32",
    FLOAT64 : "f64"
}

VOID_TYPE = IntType(0, True)
VOID_TYPE_NAME = "void"

DEFAULT_INT_TYPE = S_INT32
DEFAULT_FLOAT_TYPE = FLOAT32
CHAR_TYPE = S_INT8
SIZE_TYPE = U_INT64

NumberType = IntType | FloatType


def cmp_int_type(itype1, itype2):
    return (
            (itype1 == itype2)
        and (getattr(itype1, "issigned") is getattr(itype2, "issigned"))
    )