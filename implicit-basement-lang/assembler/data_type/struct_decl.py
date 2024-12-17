from collections import OrderedDict
from .data_type import DataType


class StructDecl(DataType):
    name:   str
    fields: OrderedDict[str, DataType]

    def __new__(cls, name: str, field_types: OrderedDict[str, DataType]):
        total_size = sum([T for T in field_types.values()])
        obj = super().__new__(cls, total_size)
        setattr(obj, "size", obj)
        setattr(obj, "name", name)
        setattr(obj, "fields", field_types.copy())
        return obj

    def get_member_sizes(self) -> tuple[DataType, ...]:
        field_dict: OrderedDict[str, DataType] = getattr(self, "fields")
        return tuple(field_dict.values())