EOL = ";"
EOF = chr(0)
COMMENT_SIGN = "#"

VAR_ATTR_STR_LIST = ["const"]
POINTER_CHAR = "*"

ASSIGN_CHAR = "="
COMMA_CHAR = ","

ARR_L_DELIM = "["
ARR_R_DELIM = "]"
ARR_MMB_DELIM = ","

STRUCT_KEYWORD = "struct"
STRUCT_L_DELIM = "{"
STRUCT_R_DELIM = "}"
STRUCT_MMB_DELIM = ","
STRUCT_MMB_ACCESS_OP = "."

FUNCTION_KEYWORD = "function"
FUNC_L_DELIM = "("
FUNC_R_DELIM = ")"
FUNC_ARG_DELIM = ","
FUNC_RET_SYMBOL = "=>"

SCOPE_START = ":"
SCOPE_START_ALT = "{"
SCOPE_END = "end"
SCOPE_END_ALT = "}"

IF_KEYWORD = "if"
ELSE_KEYWORD = "else"
END_IF_KEYWORD = "if"

LOOP_KEYWORD = "loop"
END_LOOP_KEYWORD = "loop"
LOOP_CONT_KEYWORD = "continue"
LOOP_BREAK_KEYWORD = "break"

SCOPE_BLOCK_KEYWORD = "block"
END_SCOPE_BLOCK_KEYWORD = "block"

RETURN_KEYWORD = "return"

EXPR_GROUP_L_DELIM = "("
EXPR_GROUP_R_DELIM = ")"

DECIMAL_PT = "."
STR_DELIM = "\""
CHAR_DELIM = "'"

ASSIGN_OP_DICT = {"ASSIGN": ASSIGN_CHAR}

L_UN_OP_DICT = {
    "PLUS"    : "+",
    "MINUS"   : "-",
    "BIT_NOT" : "~",
    "LGC_NOT" : "!",
    "DEREF"   : "*",
    "REF"     : "&",
    "INC"     : "++",
    "DEC"     : "--",
}
L_UN_OP__TCAST_L_DELIM = "("
L_UN_OP__TCAST_R_DELIM = ")"

AMBIGIOUS_L_UN_OPS = {"PLUS", "MINUS", "REF", "DEREF"}


R_UN_OP_DICT = {
    "INC" : "++",
    "DEC" : "--"
}


ARITH_BIN_OP_DICT = {
    "term" : {
        "ADD" : "+",
        "SUB" : "-",
    },
    "factor" : {
        "MUL" : "*",
        "DIV" : "/",
        "MOD" : "%",
    }
}


BIT_BIN_OP_DICT = {
    "term" : {
        "OR"    : "|",
        "XOR"   : "^",
        "LSHFT" : "<<",
        "RSHFT" : ">>",
    },
    "factor" : { "AND" : "&", }
}


REL_BIN_OP_DICT = {
    "LESS" : "<",
    "LEQ"  : "<=",
    "GRTR" : ">",
    "GEQ"  : ">=",
    "EQ"   : "==",
    "NEQ"  : "!=",
}


BIN_OP_DICT = (
      ARITH_BIN_OP_DICT["term"]
    | ARITH_BIN_OP_DICT["factor"]
    | BIT_BIN_OP_DICT["term"]
    | BIT_BIN_OP_DICT["factor"]
    | REL_BIN_OP_DICT
)

TERM_OP_DICT = (
      ARITH_BIN_OP_DICT["term"] | BIT_BIN_OP_DICT["term"] | REL_BIN_OP_DICT
    | ASSIGN_OP_DICT
)

FACTOR_OP_DICT = (
    ARITH_BIN_OP_DICT["factor"] | BIT_BIN_OP_DICT["factor"]
)