from ..data_type.struct_decl  import StructDecl
from ..data_type.types        import DataType, get_data_type_name

from ..error import TokenizeError, ParseError

from .token  import Token

from dataclasses import dataclass, field
from typing      import Optional


VAR_ATTR_STR_LIST = ("const", )


@dataclass
class Variable(Token):
    name:      str
    data_type: DataType
    attrib:    str | None = field(default=None)

    def __post_init__(self):
        self.size = getattr(self.data_type, "size")
        self.value_token = Token()

    def update(self, attrib: Optional[str] = None) -> None:
        if attrib is not None:
            if attrib not in VAR_ATTR_STR_LIST:
                raise TokenizeError(f"\"{attrib}\" is not a valid variable"
                                    " attribute")
            self.attrib = attrib

    def __str__(self) -> str:
        return (f"{self.__class__.__name__}(\"{self.name}\", "
                f"type={get_data_type_name(self.data_type)})")


@dataclass
class VariableInvoke(Token):
    name : str
    var  : Variable | None = field(init=False, default=None)

    def __str__(self) -> str:
        return f"{self.__class__.__name__}(\"{self.name}\")"


@dataclass
class StructMemberInvoke(Token):
    name:   str
    __struct: StructDecl | None = field(init=False, default=None)
    __offset: int               = field(init=False, default=0)

    @property
    def struct(self) -> StructDecl:
        if self.__struct:
            return self.__struct
        raise AttributeError(
            f"Struct member name \"{self.name}\" doest not have an "
            "associated struct yet"
        )
    
    @struct.setter
    def struct(self, _struct: StructDecl):
        if self.name not in _struct.members:
            raise ParseError(
                f"\"{self.name}\" is not a member of struct \"{_struct.name}\""
            )
        
        self.__offset = int(_struct.members[self.name])
        self.__struct = _struct
    
    @property
    def offset(self) -> int:
        return self.__offset

    def __str__(self) -> str:
        if self.__struct:
            struct_name = self.__struct.name
        else:
            struct_name = "?"
        return f"[{struct_name}].{self.name}"