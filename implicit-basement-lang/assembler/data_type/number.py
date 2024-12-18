from .data_type import DataType


class IntType(DataType):
    issigned: bool

    def __new__(cls, size: int, issigned: bool, name: str):
        obj = super().__new__(cls, size)
        
        setattr(obj, "size", obj)
        setattr(obj, "issigned", issigned)
        setattr(obj, "name", name)
        
        return obj


class FloatType(DataType):
    def __new__(cls, size, name: str):
        obj = super().__new__(cls, size)
        
        setattr(obj, "size", obj)
        setattr(obj, "name", name)
        
        return obj


S_INT8    = IntType(1, True,  "i8")
S_INT16   = IntType(2, True,  "i16")
S_INT32   = IntType(4, True,  "i32")
S_INT64   = IntType(8, True,  "i64")
U_INT8    = IntType(1, False, "u8")
U_INT16   = IntType(2, False, "u16")
U_INT32   = IntType(4, False, "u32")
U_INT64   = IntType(8, False, "u64")
U_INTSIZE = IntType(8, False, "usize")
FLOAT32 = FloatType(4, "f32")
FLOAT64 = FloatType(8, "f64")

INT_TYPES = (
    S_INT8,
    S_INT16,
    S_INT32,
    S_INT64,
    U_INT8,
    U_INT16,
    U_INT32,
    U_INT64,
    U_INTSIZE
)
FLOAT_TYPES = (FLOAT32, FLOAT64)

VOID_TYPE = IntType(0, True, "void")

DEFAULT_INT_TYPE   = S_INT32
DEFAULT_FLOAT_TYPE = FLOAT32
CHAR_TYPE = S_INT8
SIZE_TYPE = U_INT64

NumberType = IntType | FloatType


def cmp_int_type(itype1, itype2):
    return (
            (itype1 == itype2)
        and (getattr(itype1, "issigned") is getattr(itype2, "issigned"))
    )