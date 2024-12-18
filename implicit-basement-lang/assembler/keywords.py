from .token.operator import (
    L_UN_OP_DICT,
    AMBIGIOUS_L_UN_OPS,
    OP_TCAST_L_DELIM,
    OP_TCAST_R_DELIM,
    R_UN_OP_DICT,
    TERM_OP_DICT,
    FACTOR_OP_DICT,
    OP_FIELD_ACCESS_CHAR,
    OP_ASSIGN_CHAR,
)
from .token.delim import (
    COMMA_CHAR,
    EXPR_GROUP_L_DELIM,
    EXPR_GROUP_R_DELIM,
    EOL
)
from .token.struct_elem import (
    STRUCT_KEYWORD,
    STRUCT_L_DELIM,
    STRUCT_R_DELIM,
    STRUCT_MMB_DELIM,
)
from .token.array_elem import (
    ARR_L_DELIM,
    ARR_R_DELIM,
    ARR_MMB_DELIM
)
from .token.scope_elem import (
    SCOPE_START,
    SCOPE_END,
    SCOPE_START_ALT,
    SCOPE_END_ALT,
    SCOPE_BLOCK_KEYWORD,
    END_SCOPE_BLOCK_KEYWORD
)
from .token.function import (
    FUNCTION_KEYWORD,
    FUNC_ARG_L_BRACKET,
    FUNC_ARG_R_BRACKET,
    FUNC_ARG_DELIM,
    FUNC_RET_SYMBOL,
    RETURN_KEYWORD
)
from .token.branch import (
    IF_KEYWORD,
    ELSE_KEYWORD,
    END_IF_KEYWORD,
    LOOP_KEYWORD,
    END_LOOP_KEYWORD,
    LOOP_CONT_KEYWORD,
    LOOP_BREAK_KEYWORD
)
from .token.variable import VAR_ATTR_STR_LIST
from .data_type.pointer import POINTER_CHAR


EOF = chr(0)
COMMENT_SIGN = "#"

DECIMAL_PT = "."
STR_DELIM = "\""
CHAR_DELIM = "'"