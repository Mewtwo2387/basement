from dataclasses import dataclass, field
from typing import Iterable
from ..data_type.data_type import DataType

ValueDict = dict[str, int | float | Iterable | DataType | None]


@dataclass
class Token:
    size: int = field(init=False, default=0)
    id:   str = field(init=False, default="")

    def update(self, **kwargs) -> None:
        raise NotImplementedError(
            "'update' method for Token not yet implemented"
        )