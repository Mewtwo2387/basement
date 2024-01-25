from dataclasses import dataclass, field
from typing import Iterable

ValueDict = dict[str, int | float | Iterable | None]


@dataclass
class Token:
    size:    int = field(init=False, default=0)
    address: int = field(init=False, default=0)

    def update(self, **kwargs) -> None:
        raise NotImplementedError(
            "'update' method for Token not yet implemented"
        )
    
    def get_value(self) -> ValueDict:
        raise NotImplementedError(
            "'get_value' method for Token not yet implemented"
        )