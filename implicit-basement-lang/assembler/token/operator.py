from .token import Token
from ..data_type.types import DataType, get_data_type_name
from dataclasses import dataclass, field

from collections import OrderedDict


OP_ASSOC_NIL = -1
OP_ASSOC_L2R = 0
OP_ASSOC_R2L = 1

@dataclass
class OpOrder:
    precedence: int
    assoc : int

    def __gt__(self, other : "OpOrder") -> bool:
        return (
                (self.precedence > other.precedence)
            or  (    self.precedence == other.precedence
                 and self.assoc == OP_ASSOC_L2R)
        )

    def __lt__(self, other: "OpOrder") -> bool:
        return (
                (self.precedence < other.precedence)
            or  (    self.precedence == other.precedence
                 and other.assoc == OP_ASSOC_L2R)
        )
    
    def __eq__(self, other: "OpOrder") -> bool:
        return self.precedence == other.precedence and self.assoc == other.assoc


# Operator names: Left Unary Operators
OP_UN_PLUS  = "UNARY PLUS"
OP_UN_MINUS = "UNARY MINUS"
OP_BIT_NOT  = "BITWISE NOT"
OP_LGC_NOT  = "LOGICAL NOT"
OP_DEREF    = "DEREFERENCE"
OP_REF      = "REFERENCE"
OP_PRE_INC  = "PRE-INCREMENT"
OP_PRE_DEC  = "PRE-DECREMENT"
OP_TCAST    = "TYPE CAST"

L_UN_OP_DICT = {
    OP_UN_PLUS  : "+",
    OP_UN_MINUS : "-",
    OP_BIT_NOT  : "~",
    OP_LGC_NOT  : "!",
    OP_DEREF    : "*",
    OP_REF      : "&",
    OP_PRE_INC  : "++",
    OP_PRE_DEC  : "--",
}
OP_TCAST_L_DELIM = "("
OP_TCAST_R_DELIM = ")"

AMBIGIOUS_L_UN_OPS = {OP_UN_PLUS, OP_UN_MINUS, OP_REF, OP_DEREF}


# Operator names: Right Unary Operators
OP_POST_INC = "POST-INCREMENT"
OP_POST_DEC = "POST-DECREMENT"

R_UN_OP_DICT = { OP_POST_INC : "++", OP_POST_DEC : "--" }


# Operator names: Binary operators
#   --- Arithmetic operators ---
OP_ADD = "ADD"
OP_SUB = "SUB"
OP_MUL = "MUL"
OP_DIV = "DIV"
OP_MOD = "MOD"

#   --- Bitwise operators ---
OP_OR    = "OR"
OP_AND   = "AND"
OP_XOR   = "XOR"
OP_LSHFT = "LEFT SHIFT"
OP_RSHFT = "RIGHT SHIFT"

#   --- Relation operator ---
OP_LESS = "LESS THAN"
OP_LEQ  = "LESS THAN OR EQUAL TO"
OP_GRTR = "GREATER THAN"
OP_GEQ  = "GREATER THAN OR EQUAL TO"
OP_EQ   = "EQUAL"
OP_NEQ  = "NOT EQUAL"

# --- Assignment Operator ---
OP_ASSIGN = "ASSIGN"
OP_ASSIGN_CHAR = "="

# --- Member Access Operator ---
OP_MMB_ACCESS = "MEMBER ACCESS"
OP_MMB_ACCESS_CHAR = "."

# --- Array Subscripting Operator ---
OP_ARR_SUBSCR = "ARRAY SUBSCRIPT"
OP_ARR_SUBSCR_CHAR = "ArrSubscr" # NOTE: This operator has no overt symbol

ARITH_BIN_OP_DICT = {
    "term" : {
        OP_ADD : "+",
        OP_SUB : "-",
    },
    "factor" : {
        OP_MUL : "*",
        OP_DIV : "/",
        OP_MOD : "%",
    }
}


BIT_BIN_OP_DICT = {
    "term" : {
        OP_OR    : "|",
        OP_XOR   : "^",
        OP_LSHFT : "<<",
        OP_RSHFT : ">>",
    },
    "factor" : { OP_AND : "&" }
}


# NOTE: OrderedDict is used here to test "<="/">=" first before ">" and "<"
REL_BIN_OP_DICT = OrderedDict([
    (OP_LEQ,  "<="),
    (OP_GEQ,  ">="),
    (OP_EQ,   "=="),
    (OP_NEQ,  "!="),
    (OP_LESS, "<" ),
    (OP_GRTR, ">" ),
])


__OTHER_BIN_OPS = OrderedDict([
    (OP_ASSIGN,     OP_ASSIGN_CHAR),
    (OP_MMB_ACCESS, OP_MMB_ACCESS_CHAR)
])


# NOTE: The assignment operator which has similar onset character with some
#       relation operators goes AFTER the relation operation dict.
TERM_OP_DICT = (
      ARITH_BIN_OP_DICT["term"]
    | BIT_BIN_OP_DICT["term"]
    | REL_BIN_OP_DICT
    | __OTHER_BIN_OPS
)

FACTOR_OP_DICT = (
    ARITH_BIN_OP_DICT["factor"] | BIT_BIN_OP_DICT["factor"]
)

ARR_SUBSCR_DICT = {OP_ARR_SUBSCR : OP_ARR_SUBSCR_CHAR}

_OP_STR_DICT = (
      TERM_OP_DICT
    | FACTOR_OP_DICT
    | L_UN_OP_DICT
    | R_UN_OP_DICT
    | ARR_SUBSCR_DICT
)


OP_PRECEDENCE = {
    OP_ASSIGN     : OpOrder( 1, OP_ASSOC_R2L),
    OP_OR         : OpOrder( 2, OP_ASSOC_L2R),
    OP_XOR        : OpOrder( 3, OP_ASSOC_L2R),
    OP_AND        : OpOrder( 4, OP_ASSOC_L2R),
    OP_EQ         : OpOrder( 5, OP_ASSOC_L2R),
    OP_NEQ        : OpOrder( 5, OP_ASSOC_L2R),
    OP_LESS       : OpOrder( 6, OP_ASSOC_L2R),
    OP_LEQ        : OpOrder( 6, OP_ASSOC_L2R),
    OP_GRTR       : OpOrder( 6, OP_ASSOC_L2R),
    OP_GEQ        : OpOrder( 6, OP_ASSOC_L2R),
    OP_LSHFT      : OpOrder( 7, OP_ASSOC_L2R),
    OP_RSHFT      : OpOrder( 7, OP_ASSOC_L2R),
    OP_ADD        : OpOrder( 8, OP_ASSOC_L2R),
    OP_SUB        : OpOrder( 8, OP_ASSOC_L2R),
    OP_MUL        : OpOrder( 9, OP_ASSOC_L2R),
    OP_DIV        : OpOrder( 9, OP_ASSOC_L2R),
    OP_MOD        : OpOrder( 9, OP_ASSOC_L2R),
    OP_REF        : OpOrder(10, OP_ASSOC_R2L),
    OP_DEREF      : OpOrder(10, OP_ASSOC_R2L),
    OP_TCAST      : OpOrder(10, OP_ASSOC_R2L),
    OP_BIT_NOT    : OpOrder(10, OP_ASSOC_R2L),
    OP_LGC_NOT    : OpOrder(10, OP_ASSOC_R2L),
    OP_UN_PLUS    : OpOrder(10, OP_ASSOC_R2L),
    OP_UN_MINUS   : OpOrder(10, OP_ASSOC_R2L),
    OP_PRE_INC    : OpOrder(10, OP_ASSOC_R2L),
    OP_PRE_DEC    : OpOrder(10, OP_ASSOC_R2L),
    OP_POST_INC   : OpOrder(11, OP_ASSOC_L2R),
    OP_POST_DEC   : OpOrder(11, OP_ASSOC_L2R),
    OP_MMB_ACCESS : OpOrder(11, OP_ASSOC_L2R),
    OP_ARR_SUBSCR : OpOrder(11, OP_ASSOC_L2R),
}


@dataclass
class AbstractOperator(Token):
    name:  str
    arity: int = field(init=False)
    order: OpOrder = field(init=False)

    def __post_init__(self):
        self.order = OP_PRECEDENCE[self.name]

    def __str__(self) -> str:
        return (f"{self.__class__.__name__}"
                f"(\"{_OP_STR_DICT[self.name]}\")")

@dataclass
class LeftUnaryOp(AbstractOperator):
    def __post_init__(self):
        super().__post_init__()
        self.arity = 1

@dataclass
class TypeCastOp(AbstractOperator):
    name: str = field(init=False, default=OP_TCAST)

    def __init__(self, to_type: DataType):
        self.to_type = to_type
    
    def __post_init__(self):
        super().__post_init__()
        self.arity = 1

    def __str__(self) -> str:
        return (f"{self.__class__.__name__}"
                f"({get_data_type_name(self.to_type)})")


@dataclass
class RightUnaryOp(AbstractOperator):
    def __post_init__(self):
        super().__post_init__()
        self.arity = 1


@dataclass
class BinaryOp(AbstractOperator):
    def __post_init__(self):
        super().__post_init__()
        self.arity = 2

@dataclass
class AssignOp(AbstractOperator):
    name: str = field(init=False, default=OP_ASSIGN)

    def __str__(self) -> str:
        return f"\"{OP_ASSIGN_CHAR}\""

@dataclass
class MemberAccessOp(AbstractOperator):
    name: str = field(init=False, default=OP_MMB_ACCESS)

    def __str__(self) -> str:
        return f"\"{OP_MMB_ACCESS_CHAR}\""