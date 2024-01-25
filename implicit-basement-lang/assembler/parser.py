from .token.token import Token
from .token.function import Function, FunctionDeclaration, FunctionCall
from .token.variable import Variable, VariableInvoke
from .token.number   import Integer, Float
from .token.string   import String
from .token.delim    import (
        ArrayDelimLeft, ArrayDelimRight, ArrayMemberDelim,
        StructDelimLeft, StructDelimRight,StructMemberDelim,
        Comma, ScopeStart, ScopeEnd
    )
from .token.branch import If, Else, Loop, LoopContinue, LoopBreak
from .token.operator import (
    AssignOp, MemberAccessOp, LeftUnaryOp, RightUnaryOp, TypeCastOp, BinaryOp
)
from .data_type.number import (
        INT_TYPE_NAME,  
        FLOAT_TYPE_NAME, 
        VOID_TYPE_NAME,  
        VOID_TYPE,
        CHAR_TYPE,
        DEFAULT_INT_TYPE,
        DEFAULT_FLOAT_TYPE,
        IntType, FloatType
    )
from .data_type.struct import Struct
from .data_type.pointer import PointerType
from .data_type.types import DataType

from .error import ParseError

from .keywords import *

from dataclasses import dataclass, field
from itertools import zip_longest
from functools import partial as func_partial
from collections import OrderedDict
from typing import Optional

struct_dict: dict[str, Struct] = {}

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
        if output_idx != 0:
            del output_list[output_idx:]

        input_idx, output_idx = self.input_idx, self.output_idx


def parse(prog_str: str) -> tuple[list[Token], dict[str, Struct]] | None:
    """
    Parse a program, i.e. of the following symbols:
        { ( decl, EOL ) | func | struct }, EOF
    """

    # Match the following symbols:
    #   { ( decl, EOL ) | func | struct }
    while True:
        brpt = BranchPoint()
        parsing_success =  (parse_decl(prog_str)
                            and match_str(prog_str, EOL, True)) \
                        or (parse_func(prog_str))               \
                        or (parse_struct(prog_str))
        if not parsing_success:
            brpt.revert_point()
            break

    # Match the symbol:  EOF
    if not match_str(prog_str, EOF):
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
    idx_start = input_idx

    skip_whitespace(prog_str)

    # First character must alphabetic
    if not prog_str[input_idx].isalpha():
        return ""
    input_idx += 1

    while input_idx < len(prog_str):
        c = prog_str[input_idx]
        if not (c.isalpha() or c.isnumeric()):
            break
        input_idx += 1

    return prog_str[idx_start:input_idx]


def parse_decl(prog_str: str) -> bool:
    """
    Parse declaration statements:
        var_decl | func_decl
    """
    return parse_var_decl(prog_str) or parse_func_decl(prog_str)


def parse_var_decl(prog_str: str) -> bool:
    """
    Parse a variable declaration:
        [ var_attrib ], type, var_id, [ var_init ], { var_id, [ var_init ] }
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
            append_to_output(Comma())

        var_name = get_id(prog_str)
        if len(var_name) > 0:
            append_to_output( Variable(var_name, var_type) )
            var_token_count += 1
            parse_var_init_token(prog_str)  # An optional structure
        else:
            brpt_loop.revert_point()
            break

    return var_token_count > 0


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


def parseget_data_type(prog_str: str) -> DataType | None:
    """
    Parse data type and obtain the output token:
        ( int_type | float_type | ( "struct", id ) | "void" ), { "*" }
    """
    brpt = BranchPoint()

    get_data_type_func_list = (
        parseget_int_data_type,
        parseget_float_data_type,
        parseget_struct_type,
        parseget_void_type
    )
    for func in get_data_type_func_list:
        data_type = func(prog_str)
        if data_type is not None:
            break
    else:
        brpt.revert_point()
        return None

    while match_str(prog_str, POINTER_CHAR, True):
        data_type = PointerType(data_type)

    return data_type


def parseget_int_data_type(prog_str: str) -> IntType | None:
    """
    Parse integer data type and obtain the resulting token:
        ( ( "u" | "i" ), ( "8" | "16" | "32" | "64" ) ) | ( "usize" )

    NOTE: No intervening whitespace
    """
    skip_whitespace(prog_str)
    for name, T in INT_TYPE_NAME.items():
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
    for name, T in FLOAT_TYPE_NAME.items():
        if match_str(prog_str, name):
            return T
    return None


def parseget_struct_type(prog_str: str) -> Struct | None:
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


def parse_var_init_token(prog_str: str) -> bool:
    """
    Parse a variable initializer:
        "=", ( literal | arr_init | struct_init )
    """
    brpt = BranchPoint()

    if not match_str(prog_str, ASSIGN_CHAR, True):
        return False
    append_to_output(AssignOp())

    initializer_token_func = (
        parse_literal,
        func_partial(parse_initializer, init_type="array"),
        func_partial(parse_initializer, init_type="struct")
    )
    for func in initializer_token_func:
        if func(prog_str):
            return True

    brpt.revert_point()
    return False


def parse_literal(prog_str: str) -> bool:
    """
    Parse a literal value:
        integer | float | char | string
    """
    lit_token_func = (
        parseget_int_literal,
        parseget_float_literal,
        parseget_char_literal,
        parseget_string_literal
    )
    for func in lit_token_func:
        lit_token = func(prog_str)
        if lit_token is not None:
            append_to_output(lit_token)
            return True

    return False


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
        raise ParseError("[Internal error] Invalid init type")
    
    brpt = BranchPoint()

    if not match_str(prog_str, ARR_L_DELIM, True):
        return False
    append_to_output(cls_l_delim())

    if parse_expr(prog_str):
        while True:
            brpt_arr_mem = BranchPoint()

            if not match_str(prog_str, ARR_MMB_DELIM, True):
                break
            append_to_output(cls_mmb_delim())

            if not parse_expr(prog_str):
                brpt_arr_mem.revert_point()
                break

    if not match_str(prog_str, ARR_R_DELIM, True):
        brpt.revert_point()
        return False
    append_to_output(cls_r_delim())

    return True


def parse_func_decl(prog_str: str) -> bool:
    """
    Parse a function declaration:
        type, id, "(", param_list, ")", { ",", id, "(", param_list, ")" }
    """
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

        if not match_str(prog_str, FUNC_L_DELIM, True):
            brpt_loop.revert_point()
            return False
        
        param_dict = parseget_param_dict(prog_str)

        if not match_str(prog_str, FUNC_R_DELIM, True):
            brpt_loop.revert_point()
            break

        append_to_output(
            FunctionDeclaration(func_name, ret_type, param_dict) 
        )
        func_token_count += 1

    return func_token_count > 0


def parseget_param_dict(prog_str: str) -> OrderedDict[str, DataType]:
    """
    Parse and get an ordered dictionary of function parameters
    """
    param_dict = OrderedDict()
    while True:
        param = parseget_param(prog_str)
        if param is not None:
            arg_name, data_type = param
            param_dict[arg_name] = data_type
        else:
            break
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


def parse_struct(prog_str: str) -> bool:
    """
    Parse a `struct` declaration:
        "struct", id, scope_start, struct_mem, { struct_mem }, scope_end,
        [ "struct" ], [ id ]
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

    match_str(prog_str, STRUCT_KEYWORD, True)   # Optional structure

    closing_struct_name = get_id(prog_str)
    if (len(closing_struct_name) > 0) and (closing_struct_name != struct_name):
        raise ParseError(
                 'Name mismatch in struct declaration: '
                f'"{struct_name}" != "{closing_struct_name}"'
            )

    struct = Struct(struct_name, struct_mmb_dict)
    struct_dict[struct_name] = struct

    return True


def parseget_struct_mmb_tuple(prog_str: str) \
        -> tuple[DataType, list[str]] | None:
    """
    Parse and obtain a struct member:
        type, id, { ",", id }, EOL
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
        [ "function" ], [ id ]
    """
    brpt = BranchPoint()

    if not match_str(prog_str, FUNCTION_KEYWORD, True):
        return False
    
    func_name = get_id(prog_str)
    if len(func_name) == 0:
        brpt.revert_point()
        return False
    
    if not match_str(prog_str, FUNC_L_DELIM, True):
        brpt.revert_point()
        return False

    param_dict = parseget_param_dict(prog_str)

    if not match_str(prog_str, FUNC_R_DELIM, True):
        brpt.revert_point()
        return False
    
    ret_type = VOID_TYPE
    if match_str(prog_str, FUNC_RET_SYMBOL, True):
        ret_type = parseget_data_type(prog_str)
        if ret_type is None:
            brpt.revert_point()
            return False

    append_to_output( Function(func_name, ret_type, param_dict) )

    if not parse_cmpd_stmt(prog_str):
        brpt.revert_point()
        return False
    
    match_str(prog_str, FUNCTION_KEYWORD, True)   # Optional structure

    closing_func_name = get_id(prog_str)
    if (len(closing_func_name) > 0) and (closing_func_name != func_name):
            raise ParseError(
                 'Name mismatch in function declaration: '
                f'"{func_name}" != "{closing_func_name}"'
            )

    return True


def parse_scope_start(prog_str: str) -> bool:
    if (       match_str(prog_str, SCOPE_START, True)
            or match_str(prog_str, SCOPE_START_ALT, True)):
        append_to_output(ScopeStart())
        return True
    return False


def parse_scope_end(prog_str: str) -> bool:
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

        if parse_var_decl(prog_str) and match_str(prog_str, EOL, True):
            parsed_rule_count += 1
            continue

        brpt_loop.revert_point()

        if not parse_stmt(prog_str):
            break
        parsed_rule_count += 1

    if (parsed_rule_count == 0) or (not parse_scope_end(prog_str)):
        brpt.revert_point()
        return False

    return True


def parse_stmt(prog_str: str) -> bool:
    """
    Parse a statement:
        if_stmt | loop_stmt | loop_ctrl | scope_block | ( [ expr ], EOL )
    """
    parse_stmt_funcs = (
        parse_if_stmt,
        parse_loop_stmt,
        parse_loop_ctrl,
        parse_scope_block,
        parse_expr_stmt
    )
    for func in parse_stmt_funcs:
        if func(prog_str):
            return True
    return False


def parse_if_stmt(prog_str: str) -> bool:
    """
    Parse an if/if-else/if-else-if statement:
        "if", "(", expr, ")", cmpd_stmt, [ "else", ( cmpd_stmt | if_stmt ) ],
        [ "if" ]
    """
    brpt = BranchPoint()

    if not match_str(prog_str, IF_KEYWORD, True):
        return False
    append_to_output(If())
    
    parse_res = (
            match_str(prog_str, FUNC_L_DELIM, True)
        and parse_expr(prog_str)
        and match_str(prog_str, FUNC_R_DELIM, True)
    )
    if not parse_res:
        brpt.revert_point()
        return False

    if not parse_cmpd_stmt(prog_str):
        brpt.revert_point()
        return False

    if match_str(prog_str, ELSE_KEYWORD, True):
        append_to_output(Else())

        parse_res = (
                parse_cmpd_stmt(prog_str)
            or  parse_if_stmt(prog_str)
        )
        if not parse_res:
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
    
    if match_str(prog_str, LOOP_CONT_KEYWORD):
        append_to_output(LoopContinue())

    if not match_str(prog_str, EOL, True):
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


def parse_expr_stmt(prog_str: str) -> bool:
    """
    Parse an expression standing as a statement:
        expr, EOL
    """
    brpt = BranchPoint()

    if not (parse_expr(prog_str) and match_str(prog_str, EOL, True)):
        brpt.revert_point()
        return False

    return True


def parse_expr(prog_str: str) -> bool:
    """
    Parse an expression, i.e. that which reduces to a single piece of data:
        literal
      | func_call
      | var_invoke
      | var_assign
      | ( l_un_op, expr )
      | ( expr, r_un_op )
      | ( expr, bin_op, expr )
      | ( "(", expr, ")" ) 
    """
    return (
            parse_literal(prog_str)
        or  parse_func_call(prog_str)
        or  parse_var_invoke(prog_str)
        or  parse_var_assign(prog_str)
        or  parse_l_un_op_expr(prog_str)
        or  parse_r_un_op_expr(prog_str)
        or  parse_bin_op_expr(prog_str)
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

    if not match_str(prog_str, FUNC_L_DELIM, True):
        brpt.revert_point()
        return False
    
    expr_count = 0
    while True:
        if expr_count > 0:
            if not match_str(prog_str, COMMA_CHAR, True):
                break
            append_to_output(Comma())

        if parse_expr(prog_str):
            expr_count += 1

    if not match_str(prog_str, FUNC_R_DELIM, True):
        brpt.revert_point()
        return False
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

    if not (    match_str(prog_str, ARR_L_DELIM, True)
            and parse_expr(prog_str)
            and match_str(prog_str, ARR_R_DELIM, True)):
        brpt.revert_point()
    
    if match_str(prog_str, ARR_L_DELIM, True):
        append_to_output(ArrayDelimLeft())

        if not (    parse_expr(prog_str)
                and match_str(prog_str, ARR_R_DELIM, True)):
            brpt.revert_point()
            return False

        append_to_output(ArrayDelimRight())
    
    if match_str(prog_str, STRUCT_MMB_ACCESS_OP, True):
        append_to_output(MemberAccessOp())

        if not parse_var_invoke(prog_str):
            brpt.revert_point()
            return False

    return True


def parse_var_assign(prog_str: str) -> bool:
    """
    Parse an assignment expression:
        id, "=", ( expr | arr_init | struct_init )
    """
    brpt = BranchPoint()

    var_name = get_id(prog_str)
    if len(var_name) == 0:
        return False
    append_to_output(VariableInvoke(var_name))

    if not match_str(prog_str, ASSIGN_CHAR, True):
        brpt.revert_point()
        return False
    append_to_output(AssignOp())

    if not (    parse_expr(prog_str)
            or  parse_initializer(prog_str, "array")
            or  parse_initializer(prog_str, "struct")):
        brpt.revert_point()
        return False
    return True


def parse_l_un_op_expr(prog_str: str) -> bool:
    """
    Parse a left unary operation expression:
        l_un_op, expr
    """
    brpt = BranchPoint()
    
    skip_whitespace(prog_str)
    for _, op_str in L_UN_OP_DICT:
        if match_str(prog_str, op_str):
            append_to_output(LeftUnaryOp(op_str))
            break
    else:
        if match_str(prog_str, L_UN_OP__TCAST_L_DELIM):
            to_type = parseget_data_type(prog_str)
            if to_type is None:
                brpt.revert_point()
                return False
            append_to_output(TypeCastOp(to_type))

            if not match_str(prog_str, L_UN_OP__TCAST_R_DELIM, True):
                brpt.revert_point()
                return False
            
    if not parse_expr(prog_str):
        brpt.revert_point()
        return False
    return True


def parse_r_un_op_expr(prog_str: str) -> bool:
    """
    Parse a right unary operation expression:
        expr, r_un_op
    """
    brpt = BranchPoint()

    if not parse_expr(prog_str):
        return False
    
    skip_whitespace(prog_str)
    for _, op_str in R_UN_OP_DICT:
        if match_str(prog_str, op_str):
            append_to_output(RightUnaryOp(op_str))
            return True
    
    brpt.revert_point()
    return False


def parse_bin_op_expr(prog_str: str) -> bool:
    """
    Parse a binary operation expression:
        expr, bin_op, expr
    """
    brpt = BranchPoint()

    if not parse_expr(prog_str):
        return False

    for _, op_str in BIN_OP_DICT:
        if match_str(prog_str, op_str):
            append_to_output(BinaryOp(op_str))
            break
    else:
        brpt.revert_point()
        return False

    if not parse_expr(prog_str):
        brpt.revert_point()
        return False

    return True


def parse_grouped_expr(prog_str: str) -> bool:
    """
    Parse a grouped expression:
        "(", expr, ")"
    """
    brpt = BranchPoint()

    if (    match_str(prog_str, EXPR_GROUP_L_DELIM, True)
        and parse_expr(prog_str)
        and match_str(prog_str, EXPR_GROUP_R_DELIM, True)):
        return True

    brpt.revert_point()
    return False


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
    

def parseget_int_literal(prog_str: str) -> Token | None:
    """
    Parse and get an integer literal
        dig_seq, [ int_type ]
    """
    brpt = BranchPoint()

    skip_whitespace(prog_str)
    digit_seq = get_digit_seq(prog_str)
    if len(digit_seq) == 0:
        brpt.revert_point()
        return None
    
    int_type = parseget_int_data_type(prog_str)
    if int_type is None:
        int_type = DEFAULT_INT_TYPE
    
    return Integer(int(digit_seq), int_type)


def parseget_float_literal(prog_str: str) -> Token | None:
    """
    Parse and get a float literal
        dig_seq, ".", [ dig_seq ], [ float_type ]
    """
    brpt = BranchPoint()

    skip_whitespace(prog_str)
    digit_seq = get_digit_seq(prog_str)
    if (len(digit_seq) == 0) and not match_str(prog_str, DECIMAL_PT) :
        brpt.revert_point()
        return None

    digit_seq += ("." + get_digit_seq(prog_str))

    float_type = parseget_float_data_type(prog_str)
    if float_type is None:
        float_type = DEFAULT_FLOAT_TYPE

    return Float(float(digit_seq), float_type)


def parseget_char_literal(prog_str: str) -> Token | None:
    """
    Parse and get a character literal:
        "'", ASCII_char, "'"
    """
    brpt = BranchPoint()

    if not match_str(prog_str, CHAR_DELIM, True):
        return None
    
    char = get_id(prog_str)
    if len(char) != 1:
        brpt.revert_point()
        return None

    if not match_str(prog_str, CHAR_DELIM, True):
        brpt.revert_point()
        return None
    
    return Integer(ord(char), CHAR_TYPE)


def parseget_string_literal(prog_str: str) -> Token | None:
    """
    Parse and get a string literal:
        '"', { ASCII_char }, '"'
    """
    brpt = BranchPoint()

    if not match_str(prog_str, STR_DELIM, True):
        return None
    
    string = get_id(prog_str)

    if not match_str(prog_str, STR_DELIM, True):
        brpt.revert_point()
        return None
    
    return String(string)