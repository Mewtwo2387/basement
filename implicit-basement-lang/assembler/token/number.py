from dataclasses import dataclass

from .data import Data
from ..data_type.number import IntType, FloatType


@dataclass
class Integer(Data):
    value: int
    type:  IntType


@dataclass
class Float(Data):
    value: float
    type:  FloatType