from .number import IntType, FloatType
from .pointer import PointerType
from .struct import Struct

DataType = IntType | FloatType | Struct | PointerType