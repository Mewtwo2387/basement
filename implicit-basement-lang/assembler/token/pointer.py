from dataclasses import dataclass

from .data import Data
from ..data_type.pointer import PointerType


@dataclass
class Pointer(Data):
    value: int  # Address of the pointer
    type:  PointerType