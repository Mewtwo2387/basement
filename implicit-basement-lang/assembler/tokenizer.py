from .token.array_elem import (
    ArrayDelimLeft, ArrayDelimRight, ArrayMemberDelim,
    ArraySubscriptDelimLeft, ArraySubscriptDelimRight
)
from .token.branch import If, Else, Loop, LoopContinue, LoopBreak
from .token.delim import (
    EndOfLine, ExprGroupDelimLeft, ExprGroupDelimRight
)
from .token.function import (
    Function, FunctionDeclaration, Return,
    ArgBracketLeft, ArgBracketRight, ArgDelim
)
from .token.number   import Integer, Float
from .token.operator import (
    AssignOp, MemberAccessOp, LeftUnaryOp, RightUnaryOp, TypeCastOp, BinaryOp,
    FunctionCall
)
from .token.scope_elem import ScopeStart, ScopeEnd
from .token.string   import String
from .token.struct_elem import (
    StructDelimLeft, StructDelimRight, StructMemberDelim
)
from .token.token    import Token
from .token.variable import Variable, VariableInvoke

from .data_type.array import Array
from .data_type.number import (
        INT_STR_TO_TYPE_DICT,  
        FLOAT_STR_TO_TYPE_DICT, 
        VOID_TYPE_NAME,  
        VOID_TYPE,
        CHAR_TYPE,
        DEFAULT_INT_TYPE,
        DEFAULT_FLOAT_TYPE,
        IntType, FloatType
    )
from .data_type.pointer import PointerType
from .data_type.struct_decl import StructDecl
from .data_type.types import DataType

from .error import TokenizeError

from .keywords import *

from collections import OrderedDict
from dataclasses import dataclass, field
from functools import partial as func_partial
from itertools import zip_longest
from typing import Optional


struct_dict: dict[str, StructDecl] = {}

input_idx: int = 0
output_list: list[Token] = []
output_idx = 0


@dataclass
class BranchPoint:
    input_idx:  int = field(init=False)
    output_idx: int = field(init=False)

    def __post_init__(self):
        self.input_idx = input_idx
        self.output_idx = output_idx
    
    def revert_point(self) -> None:
        global input_idx, output_idx, output_list
        if len(output_list) > 0:
            del output_list[self.output_idx:]

        input_idx, output_idx = self.input_idx, self.output_idx


def tokenize(prog_str: str) -> tuple[list[Token], dict[str, StructDecl]] | None:
    """
    Tokenize a program, i.e. of the following symbols:
        { decl | func | struct }, EOF
    """
    while True:
        brpt = BranchPoint()
        parsing_success =  (parse_comment(prog_str)) \
                        or (parse_decl(prog_str))    \
                        or (parse_func(prog_str))    \
                        or (parse_struct_decl(prog_str))
        if not parsing_success:
            brpt.revert_point()
            break

    if not match_str(prog_str, EOF, True):
        return None

    return output_list, struct_dict


def skip_whitespace(prog_str: str) -> None:
    global input_idx
    while input_idx < len(prog_str) and prog_str[input_idx].isspace():
        input_idx += 1


def append_to_output(_input: Token) -> None:
    global output_list, output_idx
    output_list.append(_input)
    output_idx += 1


def match_str(prog_str: str, matched_str: str,
              skip_left_padding: Optional[bool] = False) -> bool:
    global input_idx

    if skip_left_padding:
        skip_whitespace(prog_str)

    str_matching = True
    for c_prog, c_match in zip_longest(prog_str[input_idx:], matched_str):
        if (c_prog is None) and (c_match is not None):
            str_matching = False
        if (not str_matching) or (c_match == None):
            break
        str_matching = (c_prog == c_match)

    if str_matching:
        input_idx += len(matched_str)
    return str_matching


def get_id(prog_str: str) -> str:
    """
    Parse and obtain the substring from the input string that
    follows the following rule for ID:
        letter, { letter | digit } ;
    """
    global input_idx

    skip_whitespace(prog_str)

    idx_start = input_idx

    # First character must alphabetic
    if not prog_str[input_idx].isalpha():
        return ""
    input_idx += 1

    while input_idx < len(prog_str):
        c = prog_str[input_idx]
        if not (c.isalpha() or c.isnumeric() or c == "_"):
            break
        input_idx += 1

    return prog_str[idx_start:input_idx]


def match_eol(prog_str: str) -> bool:
    if not match_str(prog_str, EOL, True):
        return False
    parse_comment(prog_str)  # Optional structure
    return True


def parse_eol(prog_str: str) -> bool:
    """
    Parse an end of line (EOL) character
    """
    if not match_eol(prog_str):
        return False

    append_to_output(EndOfLine())
    return True


def parse_comment(prog_str: str) -> bool:
    """
    Optionally parse a comment.
    """
    global input_idx

    if not match_str(prog_str, COMMENT_SIGN, True):
        return False

    while input_idx < len(prog_str):
        if prog_str[input_idx] == "\n":
            break
        input_idx += 1
    return True


def parse_decl(prog_str: str) -> bool:
    """
    Parse declaration statements:
        var_decl | func_decl
    """
    return parse_var_decl(prog_str) or parse_func_decl(prog_str)


def parse_var_decl(prog_str: str) -> bool:
    """
    Parse a variable declaration:
        [ var_attrib ], type, id, [ var_init ], { id, [ var_init ] },
        EOL
    """
    brpt = BranchPoint()

    var_attrib_str = parseget_var_attrib_str(prog_str)
    if var_attrib_str is not None:
        pass    # TODO: Do something about variable attributes

    var_type = parseget_data_type(prog_str)
    if var_type is None:
        brpt.revert_point()
        return False

    var_token_count = 0
    while True:
        brpt_loop = BranchPoint()

        if var_token_count > 0:
            if not match_str(prog_str, COMMA_CHAR, True):
                break

        var_name = get_id(prog_str)
        if len(var_name) == 0:
            brpt_loop.revert_point()
            break

        append_to_output( Variable(var_name, var_type) )
        append_to_output( EndOfLine() )

        var_token_count += 1

        # Defer the parsing of variable initializer.
        parse_var_init_token(prog_str, var_name)  # An optional structure

    if (not match_eol(prog_str)) or (var_token_count == 0):
        brpt.revert_point()
        return False

    return True


def parseget_var_attrib_str(prog_str: str) -> str | None:
    """
    Parse variable attribute and obtain the matched string:
        "const"
    """
    skip_whitespace(prog_str)
    for var_attrib in VAR_ATTR_STR_LIST:
        if match_str(prog_str, var_attrib):
            return var_attrib
    return None


def parseget_int_data_type(prog_str: str) -> IntType | None:
    """
    Parse integer data type and obtain the resulting token:
        ( ( "u" | "i" ), ( "8" | "16" | "32" | "64" ) ) | ( "usize" )

    NOTE: No intervening whitespace
    """

    skip_whitespace(prog_str)
    for name, T in INT_STR_TO_TYPE_DICT.items():
        if match_str(prog_str, name):
            return T
    return None


def parseget_float_data_type(prog_str: str) -> FloatType | None:
    """
    Parse float data type and obtain the resulting token:
        "f", ( "32" | "64" )

    NOTE: No intervening whitespace
    """
    skip_whitespace(prog_str)
    for name, T in FLOAT_STR_TO_TYPE_DICT.items():
        if match_str(prog_str, name):
            return T
    return None


def parseget_struct_type(prog_str: str) -> StructDecl | None:
    """
    Parse struct type and obtain the resulting token:
        "struct", id
    """
    if not match_str(prog_str, STRUCT_KEYWORD, True):
        return None

    skip_whitespace(prog_str)
    struct_name = get_id(prog_str)

    return struct_dict.get(struct_name)


def parseget_void_type(prog_str: str) -> IntType | None:
    """
    Parse void type and obtain the resulting token:
        "void"
    """
    if match_str(prog_str, VOID_TYPE_NAME, True):
        return VOID_TYPE
    return None


_DATA_TYPE_PARSEGET_FUNCS = (
    parseget_int_data_type,
    parseget_float_data_type,
    parseget_struct_type,
    parseget_void_type
)
def parseget_data_type(prog_str: str) -> DataType | None:
    """
    Parse data type and obtain the output token:
        ( int_type | float_type | ( "struct", id ) | "void" ),
        [ "[", integer, "]" ]{ "*" }
    """
    brpt = BranchPoint()

    for func in _DATA_TYPE_PARSEGET_FUNCS:
        data_type = func(prog_str)
        if data_type is not None:
            break
    else:
        brpt.revert_point()
        return None

    if match_str(prog_str, ARR_L_DELIM, True):
        # Get the length of the array
        skip_whitespace(prog_str)
        arr_len_str = get_digit_seq(prog_str)

        if len(arr_len_str) == 0 or not match_str(prog_str, ARR_R_DELIM, True):
            brpt.revert_point()
            return None

        data_type = Array(data_type, int(arr_len_str))


    while match_str(prog_str, POINTER_CHAR, True):
        data_type = PointerType(data_type)

    return data_type


def parse_var_init_token(prog_str: str, var_name: str) -> bool:
    """
    Parse a variable initializer:
        "=", literal
    """
    brpt = BranchPoint()

    append_to_output( VariableInvoke(var_name) )

    if not (parse_assign_op(prog_str) and parse_literal(prog_str)):
        brpt.revert_point()
        return False

    append_to_output( EndOfLine() )

    return True


def parse_initializer(prog_str: str, init_type: str) -> bool:
    """
    Parse a general initializer:
        left_delim, [ expr, { mmb_delim, expr } ], right_delim
    """
    if init_type.casefold() == "array":
        cls_l_delim, cls_r_delim = ArrayDelimLeft, ArrayDelimRight
        cls_mmb_delim = ArrayMemberDelim
    elif init_type.casefold() == "struct":
        cls_l_delim, cls_r_delim = StructDelimLeft, StructDelimRight
        cls_mmb_delim = StructMemberDelim
    else:
        raise TokenizeError("[Internal error] Invalid init type")
    
    brpt = BranchPoint()

    if not match_str(prog_str, cls_l_delim.char, True):
        return False
    append_to_output(cls_l_delim())

    if parse_expr(prog_str):
        while True:
            brpt_arr_mem = BranchPoint()

            if not match_str(prog_str, cls_mmb_delim.char, True):
                break
            append_to_output(cls_mmb_delim())

            if not parse_expr(prog_str):
                brpt_arr_mem.revert_point()
                break

    if not match_str(prog_str, cls_r_delim.char, True):
        brpt.revert_point()
        return False

    append_to_output(cls_r_delim())

    return True


def parse_func_decl(prog_str: str) -> bool:
    """
    Parse a function declaration:
        type, id, "(", param_list, ")", { ",", id, "(", param_list, ")" }, EOL
    """
    brpt = BranchPoint()

    ret_type = parseget_data_type(prog_str)
    if ret_type is None:
        return False
    
    func_token_count = 0
    while True:
        brpt_loop = BranchPoint()

        if func_token_count > 0:
            if not match_str(prog_str, COMMA_CHAR, True):
                break

        func_name = get_id(prog_str)
        if len(func_name) == 0:
            brpt_loop.revert_point()
            return False

        if not match_str(prog_str, FUNC_ARG_L_BRACKET, True):
            brpt_loop.revert_point()
            return False

        arg_list = parseget_param_list(prog_str)

        if not match_str(prog_str, FUNC_ARG_R_BRACKET, True):
            brpt_loop.revert_point()
            break

        append_to_output(
            FunctionDeclaration(func_name, ret_type, arg_list) 
        )
        func_token_count += 1
    
    if not parse_eol(prog_str) or (func_token_count == 0):
        brpt.revert_point()
        return False

    return True


def parseget_param_list(prog_str: str) -> list[Variable]:
    """
    Parse and get an ordered dictionary of function parameters
    """
    param_dict = []

    param_count = 0
    while True:
        if param_count > 0:
            if not match_str(prog_str, COMMA_CHAR, True):
                break

        param = parseget_param(prog_str)
        if param is not None:
            arg_name, data_type = param
            param_dict.append(Variable(arg_name, data_type))
        else:
            break
        param_count += 1
    return param_dict


def parseget_param(prog_str: str) -> tuple[str, DataType] | None:
    """
    Parse and get a function parameter
    """
    brpt = BranchPoint()
    data_type = parseget_data_type(prog_str)
    if data_type is None:
        return None

    arg_name = get_id(prog_str)
    if len(arg_name) == 0:
        brpt.revert_point()
        return None
    
    return arg_name, data_type


def parse_struct_decl(prog_str: str) -> bool:
    """
    Parse a `struct` declaration:
        "struct", id, scope_start, struct_mem, { struct_mem }, scope_end,
        [ "struct", id ]
    """
    brpt = BranchPoint()
    if not match_str(prog_str, STRUCT_KEYWORD, True):
        return False
    
    struct_name = get_id(prog_str)
    if len(struct_name) == 0:
        brpt.revert_point()
        return False

    if not match_str(prog_str, STRUCT_L_DELIM, True):
        brpt.revert_point()
        return False

    struct_mmb_dict = OrderedDict()
    while True:
        struct_mmb_tuple = parseget_struct_mmb_tuple(prog_str)
        if struct_mmb_tuple is None:
            break
        else:
            if not match_eol(prog_str):
                brpt.revert_point()
                return False

            data_type, mmb_name_list = struct_mmb_tuple
            for mmb_name in mmb_name_list:
                struct_mmb_dict[mmb_name] = data_type
    
    if len(struct_mmb_dict) == 0:
        brpt.revert_point()
        return False

    if (   (len(struct_mmb_dict) == 0)
        or (not match_str(prog_str, STRUCT_R_DELIM, True)) ):
        brpt.revert_point()
        return False

    # Optional structure: [ "struct", id ]
    if match_str(prog_str, STRUCT_KEYWORD, True):
        closing_struct_name = get_id(prog_str)
        if closing_struct_name != struct_name:
            raise TokenizeError(
                    'Name mismatch in struct declaration: '
                    f'"{struct_name}" != "{closing_struct_name}"'
                )

    struct = StructDecl(struct_name, struct_mmb_dict)
    struct_dict[struct_name] = struct

    return True


def parseget_struct_mmb_tuple(prog_str: str) \
        -> tuple[DataType, list[str]] | None:
    """
    Parse and obtain a struct member:
        type, id, { ",", id }
    """
    brpt = BranchPoint()

    data_type = parseget_data_type(prog_str)
    if data_type is None:
        return None
    
    mmb_name_list = []
    while True:
        mmb_name = get_id(prog_str)
        if len(mmb_name) > 0:
            mmb_name_list.append(mmb_name)
        else:
            break

    if len(mmb_name_list) == 0:
        brpt.revert_point()
        return None
    
    return data_type, mmb_name_list


def parse_func(prog_str: str) -> bool:
    """
    Parse a function:
        "function", id, "(", [ param_list ], ")", [ "=>", type ], cmpd_stmt,
        [ "function", id ]
    """
    brpt = BranchPoint()

    if not match_str(prog_str, FUNCTION_KEYWORD, True):
        return False
    
    func_name = get_id(prog_str)
    if len(func_name) == 0:
        brpt.revert_point()
        return False
    
    if not match_str(prog_str, FUNC_ARG_L_BRACKET, True):
        brpt.revert_point()
        return False

    param_list = parseget_param_list(prog_str)

    if not match_str(prog_str, FUNC_ARG_R_BRACKET, True):
        brpt.revert_point()
        return False
    
    ret_type = VOID_TYPE
    if match_str(prog_str, FUNC_RET_SYMBOL, True):
        ret_type = parseget_data_type(prog_str)
        if ret_type is None:
            brpt.revert_point()
            return False

    append_to_output( Function(func_name, ret_type, param_list) )

    if not parse_cmpd_stmt(prog_str):
        brpt.revert_point()
        return False
    
    # Optional structure: [ "function", id ]
    if match_str(prog_str, FUNCTION_KEYWORD, True):
        closing_func_name = get_id(prog_str)
        if closing_func_name != func_name:
            raise TokenizeError(
                    'Name mismatch in function declaration: '
                    f'"{func_name}" != "{closing_func_name}"'
                )
    return True


def parse_scope_start(prog_str: str) -> bool:
    """
    Parse a starting delimiter for a scope
    """
    if (       match_str(prog_str, SCOPE_START, True)
            or match_str(prog_str, SCOPE_START_ALT, True)):
        append_to_output(ScopeStart())
        return True
    return False


def parse_scope_end(prog_str: str) -> bool:
    """
    Parse an ending delimiter for a scope
    """
    if (       match_str(prog_str, SCOPE_END, True)
            or match_str(prog_str, SCOPE_END_ALT, True)):
        append_to_output(ScopeEnd())
        return True
    return False


def parse_cmpd_stmt(prog_str: str) -> bool:
    """
    Parse compound statements delimited by scope delimiters:
        scope_start, { ( var_decl, EOL ) | stmt }, scope_end
    """
    brpt = BranchPoint()

    if not parse_scope_start(prog_str):
        return False

    parsed_rule_count = 0
    while True:
        brpt_loop = BranchPoint()

        if parse_var_decl(prog_str) or parse_stmt(prog_str):
            parsed_rule_count += 1
            continue

        brpt_loop.revert_point()
        break

    if (parsed_rule_count == 0) or (not parse_scope_end(prog_str)):
        brpt.revert_point()
        return False

    return True


def parse_if_stmt(prog_str: str) -> bool:
    """
    Parse an if/if-else/if-else-if statement:
        "if", "(", expr, ")", scope_start, { stmt },
        { "else", [ "if", "(", expr, ")" ], scope_start, { stmt } },
        scope_end, [ "if" ]
    """
    brpt = BranchPoint()

    if not match_str(prog_str, IF_KEYWORD, True):
        return False
    append_to_output(If())
    
    if_cond_parse_res = (
            match_str(prog_str, EXPR_GROUP_L_DELIM, True)
        and parse_expr(prog_str)
        and match_str(prog_str, EXPR_GROUP_R_DELIM, True)
    )
    if not if_cond_parse_res:
        brpt.revert_point()
        return False

    # Parse statements
    if not parse_scope_start(prog_str):
        brpt.revert_point()
        return False
    while parse_stmt(prog_str):
        pass

    while match_str(prog_str, ELSE_KEYWORD, True):
        # Insert an invisible ending scope delimter
        append_to_output(ScopeEnd())
        append_to_output(Else())

        # Parse for an optional else if statement
        if match_str(prog_str, IF_KEYWORD, True):
            elif_cond_parse_res = (
                    match_str(prog_str, EXPR_GROUP_L_DELIM, True)
                and parse_expr(prog_str)
                and match_str(prog_str, EXPR_GROUP_R_DELIM, True)
            )
            if not elif_cond_parse_res:
                brpt.revert_point()
                return False
            append_to_output(If())
        
        # Parse statements for the else/else-if construct.
        if not parse_scope_start(prog_str):
            brpt.revert_point()
            return False
        while parse_stmt(prog_str):
            pass

    if not parse_scope_end(prog_str):
        brpt.revert_point()
        return False
    
    match_str(prog_str, END_IF_KEYWORD, True)   # Optional structure

    return True


def parse_loop_stmt(prog_str: str) -> bool:
    """
    Parse a loop statement:
        "loop", cmpd_stmt, [ "loop" ]
    """
    brpt = BranchPoint()

    if not match_str(prog_str, LOOP_KEYWORD, True):
        return False
    append_to_output(Loop())

    if not parse_cmpd_stmt(prog_str):
        brpt.revert_point()
        return False

    match_str(prog_str, END_LOOP_KEYWORD, True)  # Optional structure
    return True


def parse_loop_ctrl(prog_str: str) -> bool:
    """
    Parse loop controls:
        ( "break" | "continue" ), EOL
    """
    brpt = BranchPoint()

    skip_whitespace(prog_str)

    if match_str(prog_str, LOOP_BREAK_KEYWORD):
        append_to_output(LoopBreak())
    elif match_str(prog_str, LOOP_CONT_KEYWORD):
        append_to_output(LoopContinue())
    else:
        return False

    if not parse_eol(prog_str):
        brpt.revert_point()
        return False
    return True


def parse_scope_block(prog_str: str) -> bool:
    """
    Parse a scope block:
        "block", cmpd_stmt, [ "block" ]
    """
    brpt = BranchPoint()

    if not match_str(prog_str, SCOPE_BLOCK_KEYWORD, True):
        return False

    if not parse_cmpd_stmt(prog_str):
        brpt.revert_point()
        return False

    match_str(prog_str, END_SCOPE_BLOCK_KEYWORD, True)  # Optional structure
    return True


def parse_return(prog_str: str) -> bool:
    """
    Parse a function return statement:
        "return", [ expr ], EOL
    """
    brpt = BranchPoint()

    if not match_str(prog_str, RETURN_KEYWORD, True):
        return False
    append_to_output(Return())
    
    parse_expr(prog_str)  # Optional structure

    if not parse_eol(prog_str):
        brpt.revert_point()
        return False
    return True


def parse_expr_stmt(prog_str: str) -> bool:
    """
    Parse an expression standing as a statement:
        expr, EOL
    """
    brpt = BranchPoint()

    if not (parse_expr(prog_str) and parse_eol(prog_str)):
        brpt.revert_point()
        return False

    return True


_STMT_PARSE_FUNCS = (
    parse_comment,
    parse_eol,
    parse_return,
    parse_loop_ctrl,
    parse_var_decl,
    parse_expr_stmt,
    parse_loop_stmt,
    parse_scope_block,
    parse_if_stmt,
)
def parse_stmt(prog_str: str) -> bool:
    """
    Parse a statement:
        if_stmt | loop_stmt | loop_ctrl | scope_block | var_decl
    |  ( [ expr ], EOL )
    """
    for func in _STMT_PARSE_FUNCS:
        if func(prog_str):
            return True
    return False


def parse_expr(prog_str: str) -> bool:
    """
    Parse an expression:
        term, [ term_op, term ]
    """
    brpt = BranchPoint()

    if not parse_term(prog_str):
        return False
    
    while parse_term_op(prog_str):
        if not parse_term(prog_str):
            brpt.revert_point()
            return False
    
    return True


def parse_term(prog_str: str) -> bool:
    """
    Parse a term in an expression:
        { l_un_op }, factor, [ factor_op, factor ], { r_un_op }
    """
    brpt = BranchPoint()

    while parse_l_un_op(prog_str):
        pass

    if not parse_factor(prog_str):
        brpt.revert_point()
        return False
    
    while parse_factor_op(prog_str):
        if not parse_factor(prog_str):
            brpt.revert_point()
            return False
    
    while parse_r_un_op(prog_str):
        pass

    return True


def parse_factor(prog_str: str) -> bool:
    """
    Parse a factor in a term:
        literal | var_invoke | func_call | ( "(", expr, ")" )
    """
    return (
            parse_literal(prog_str)
        or  parse_func_call(prog_str)
        or  parse_var_invoke(prog_str)
        or  parse_grouped_expr(prog_str)
    )

def parse_func_call(prog_str: str) -> bool:
    """
    Parse a function call expression:
        id, "(", [ expr, { ",", expr } ], ")"
    """
    brpt = BranchPoint()

    func_name = get_id(prog_str)
    if len(func_name) == 0:
        return False
    
    append_to_output(FunctionCall(func_name))

    if not match_str(prog_str, FUNC_ARG_L_BRACKET, True):
        brpt.revert_point()
        return False
    append_to_output(ArgBracketLeft())
    
    expr_count = 0
    while True:
        if expr_count > 0:
            if not match_str(prog_str, COMMA_CHAR, True):
                break
            append_to_output(ArgDelim())

        if parse_expr(prog_str):
            expr_count += 1

    if not match_str(prog_str, FUNC_ARG_R_BRACKET, True):
        brpt.revert_point()
        return False
    append_to_output(ArgBracketRight())

    return True


def parse_var_invoke(prog_str: str) -> bool:
    """
    Parse a variable invocation:
        id, [ "[", expr, "]" ], [ ".", var_invoke ]
    """
    brpt = BranchPoint()

    var_name = get_id(prog_str)
    if len(var_name) == 0:
        return False
    append_to_output(VariableInvoke(var_name))

    if match_str(prog_str, ARR_L_DELIM, True):
        append_to_output(ArraySubscriptDelimLeft())

        if not (    parse_expr(prog_str)
                and match_str(prog_str, ARR_R_DELIM, True)):
            brpt.revert_point()
            return False

        append_to_output(ArraySubscriptDelimRight())
    
    if match_str(prog_str, OP_MMB_ACCESS_CHAR, True):
        append_to_output(MemberAccessOp())

        if not parse_var_invoke(prog_str):
            brpt.revert_point()
            return False

    return True


def parse_term_op(prog_str: str) -> bool:
    """
    Parse a term operator.
    """
    skip_whitespace(prog_str)
    for op_name, op_str in TERM_OP_DICT.items():
        if match_str(prog_str, op_str):
            append_to_output(BinaryOp(op_name))
            return True

    return False


def parse_assign_op(prog_str: str) -> bool:
    """
    Parse an assignment operator
    """
    if not match_str(prog_str, OP_ASSIGN_CHAR, True):
        return False

    append_to_output(AssignOp())
    return True


def parse_factor_op(prog_str: str) -> bool:
    """
    Parse a factor operator.
    """
    skip_whitespace(prog_str)
    for op_name, op_str in FACTOR_OP_DICT.items():
        if match_str(prog_str, op_str):
            append_to_output(BinaryOp(op_name))
            return True
    return False


# Token types that cannot be to the left of ambigious left unary operators.
_INVALID_PREV_TOK__L_UN_OP = {
    Integer, Float, String, FunctionCall, VariableInvoke, ExprGroupDelimRight,
    RightUnaryOp
}

def is_valid_for_l_un_op() -> bool:
    """
    Check if a left unary operator is valid given the previous tokens:
        It is valid if there are no operands to the left of the unary operator.
        Since operands can be enclosed with parentheses, there must not be a
        right parenthesis to the left of the operator.
    """
    return (   (output_idx == 0)
            or (not type(output_list[-1]) in _INVALID_PREV_TOK__L_UN_OP))


def parse_l_un_op(prog_str: str) -> bool:
    """
    Optionally parse a left unary operator:
        "+" | "-" | "~" | "!" | "*" | "&" | "++" | "--" | ( "(", type, ")" )
    """
    brpt = BranchPoint()
    
    skip_whitespace(prog_str)
    for op_name, op_str in L_UN_OP_DICT.items():
        if not match_str(prog_str, op_str):
            continue

        if (op_name in AMBIGIOUS_L_UN_OPS) and (not is_valid_for_l_un_op()):
            continue

        append_to_output(LeftUnaryOp(op_name))
        return True

    if match_str(prog_str, OP_TCAST_L_DELIM):
        to_type = parseget_data_type(prog_str)
        if to_type is None:
            brpt.revert_point()
            return False
        append_to_output(TypeCastOp(to_type))

        if not match_str(prog_str, OP_TCAST_R_DELIM, True):
            brpt.revert_point()
            return False
        return True

    return False


def parse_r_un_op(prog_str: str) -> bool:
    """
    Optionally parse a right unary operation expression:
        "++" | "--"
    """
    brpt = BranchPoint()

    skip_whitespace(prog_str)
    for op_name, op_str in R_UN_OP_DICT.items():
        if match_str(prog_str, op_str):
            append_to_output(RightUnaryOp(op_name))
            return True
    
    brpt.revert_point()
    return False


def parse_grouped_expr(prog_str: str) -> bool:
    """
    Parse a grouped expression:
        "(", expr, ")"
    """
    brpt = BranchPoint()

    if not match_str(prog_str, EXPR_GROUP_L_DELIM, True):
        return False
    append_to_output(ExprGroupDelimLeft())

    if not parse_expr(prog_str):
        brpt.revert_point()
        return False

    if not match_str(prog_str, EXPR_GROUP_R_DELIM, True):
        brpt.revert_point()
        return False
    append_to_output(ExprGroupDelimRight())

    return True


def get_digit_seq(prog_str: str) -> str:
    """
    Parse and obtain a sequence of digits from the input string
    """
    global input_idx
    next_idx = input_idx

    while prog_str[next_idx].isdigit():
        next_idx += 1

    digit_seq = prog_str[input_idx: next_idx]
    input_idx = next_idx

    return digit_seq
    

def parse_int_literal(prog_str: str) -> bool:
    """
    Parse and get an integer literal
        dig_seq, [ int_type ]
    """
    brpt = BranchPoint()

    skip_whitespace(prog_str)
    digit_seq = get_digit_seq(prog_str)
    if len(digit_seq) == 0:
        brpt.revert_point()
        return False
    
    int_type = parseget_int_data_type(prog_str)
    if int_type is None:
        int_type = DEFAULT_INT_TYPE
    
    append_to_output(Integer(int(digit_seq), int_type))

    return True


def parse_float_literal(prog_str: str) -> bool:
    """
    Parse and get a float literal
        dig_seq, ".", [ dig_seq ], [ float_type ]
    """
    brpt = BranchPoint()

    skip_whitespace(prog_str)
    digit_seq = get_digit_seq(prog_str)
    if (len(digit_seq) == 0) and not match_str(prog_str, DECIMAL_PT) :
        brpt.revert_point()
        return False

    digit_seq += ("." + get_digit_seq(prog_str))

    float_type = parseget_float_data_type(prog_str)
    if float_type is None:
        float_type = DEFAULT_FLOAT_TYPE

    append_to_output(Float(float(digit_seq), float_type))

    return True


def parse_char_literal(prog_str: str) -> bool:
    """
    Parse and get a character literal:
        "'", ASCII_char, "'"
    """
    brpt = BranchPoint()

    if not match_str(prog_str, CHAR_DELIM, True):
        return False
    
    char = get_id(prog_str)
    if len(char) != 1:
        brpt.revert_point()
        return False

    if not match_str(prog_str, CHAR_DELIM, True):
        brpt.revert_point()
        return False
    
    append_to_output(Integer(ord(char), CHAR_TYPE))

    return True


def parse_string_literal(prog_str: str) -> bool:
    """
    Parse and get a string literal:
        '"', { ASCII_char }, '"'
    """
    brpt = BranchPoint()

    if not match_str(prog_str, STR_DELIM, True):
        return False
    
    string = get_id(prog_str)

    if not match_str(prog_str, STR_DELIM, True):
        brpt.revert_point()
        return False
    
    append_to_output(String(string))

    return True


_LITERAL_PARSE_FUNCS = (
    parse_int_literal,
    parse_float_literal,
    parse_char_literal,
    parse_string_literal,
    func_partial(parse_initializer, init_type="array"),
    func_partial(parse_initializer, init_type="struct")
)
def parse_literal(prog_str: str) -> bool:
    """
    Parse a literal value:
        integer | float | char | string | struct_init | array_init
    """
    for func in _LITERAL_PARSE_FUNCS:
        if func(prog_str):
            return True

    return False