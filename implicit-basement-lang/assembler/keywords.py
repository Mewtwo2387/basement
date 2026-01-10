from .token.operator import (
    L_UN_OP_DICT,
    AMBIGIOUS_L_UN_OPS,
    OP_TCAST_L_DELIM,
    OP_TCAST_R_DELIM,
    R_UN_OP_DICT,
    TERM_OP_DICT,
    FACTOR_OP_DICT,
    OP_MMB_ACCESS_CHAR,
    OP_ASSIGN_CHAR,
)
from .token.delim import (
    COMMA_CHAR,
    EXPR_GROUP_L_DELIM,
    EXPR_GROUP_R_DELIM,
    STRUCT_KEYWORD,
    STRUCT_MMB_DELIM,
    EOL
)
from .token.array_elem import (
    ARR_L_DELIM,
    ARR_R_DELIM,
)
from .token.initializer import (
    INITIALIZER_L_DELIM,
    INITIALIZER_R_DELIM,
    INITIALIZER_MMB_DELIM
)
from .token.scope_elem import (
    SCOPE_START_KEYWORD,
    SCOPE_END_KEYWORD
)
from .token.block import (
    BLOCK_KEYWORD,
    END_BLOCK_KEYWORD
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


EOF = chr(0)
COMMENT_SIGN = "#"

DECIMAL_PT = "."
STR_DELIM = "\""
CHAR_DELIM = "'"