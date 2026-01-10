from collections import OrderedDict
from .data_type import DataType


class StructDecl(DataType):
    members: OrderedDict[str, DataType]

    def __new__(cls, name: str, member_types: OrderedDict[str, DataType]):
        total_size = sum([T for T in member_types.values()])
        obj = super().__new__(cls, total_size)

        setattr(obj, "size", obj)
        setattr(obj, "name", name)
        setattr(obj, "members", member_types.copy())

        return obj

    def get_member_sizes(self) -> tuple[DataType, ...]:
        mmb_dict: OrderedDict[str, DataType] = getattr(self, "members")
        return tuple(mmb_dict.values())