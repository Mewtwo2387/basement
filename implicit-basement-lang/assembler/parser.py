from .token.array_elem import (
    ArrayDelimLeft, ArrayDelimRight, ArrayMemberDelim,
    ArraySubscriptDelimLeft, ArraySubscriptDelimRight
)
from .token.branch     import If, Else, Loop, LoopBreak, LoopContinue
from .token.delim import (
    ExprGroupDelimLeft, ExprGroupDelimRight, EndOfLine
)
from .token.function   import (
    Function, FunctionDeclaration,
    ArgBracketLeft, ArgBracketRight, ArgDelim, Return
)
from .token.number     import Integer, Float
from .token.operator import (
    LeftUnaryOp, RightUnaryOp, BinaryOp, TypeCastOp, AssignOp, MemberAccessOp,
    AbstractOperator, FunctionCall, OP_ARR_SUBSCR
)
from .token.scope_elem import ScopeStart, ScopeEnd
from .token.token      import Token
from .token.variable   import Variable, VariableInvoke

from .data_type.struct import Struct

from .error import ParseError

from collections import OrderedDict
from typing import Optional, Union


ScopeType = OrderedDict[str, Union[Variable, "ScopeType"]]

scope: ScopeType = OrderedDict()
SCOPE_RETURN_KEY = "_"
SCOPE_KEY_PREFIX__FUNC = "func_"
SCOPE_KEY_PREFIX__IF   = "if_"
SCOPE_KEY_PREFIX__LOOP = "loop_"

func_dict: dict[str, Function] = {}
func_decl_dict: dict[str, FunctionDeclaration] = {}


def init_global_scope():
    global scope
    if scope:
        scope = OrderedDict()


def register_new_scope(
        curr_scope: ScopeType,
        name: str,
        local_var_list: Optional[list[Variable]] = None
    ) -> None:

    new_scope: ScopeType = OrderedDict({SCOPE_RETURN_KEY : curr_scope})
    if local_var_list is not None:
        for var_token in local_var_list:
            new_scope[var_token.name] = var_token
    curr_scope[name] = new_scope


def return_to_parent_scope(curr_scope: ScopeType) -> None:
    if SCOPE_RETURN_KEY in curr_scope:
        parent_scope = curr_scope[SCOPE_RETURN_KEY]
        if not isinstance(parent_scope, OrderedDict):
            raise ParseError("Parent scope is not a valid scope")
        curr_scope = parent_scope
    else:
        if curr_scope is scope:
            raise ParseError("Attempted to backtrack from the global scope")
        raise ParseError("Current scope has no pointer to its parent scope")


def var_in_scope(curr_scope: ScopeType, var_token: VariableInvoke) -> bool:
    __curr_scope: ScopeType = curr_scope

    while SCOPE_RETURN_KEY in __curr_scope:
        if var_token.name not in __curr_scope:
            parent_scope = __curr_scope[SCOPE_RETURN_KEY]
            if not isinstance(parent_scope, OrderedDict):
                raise ParseError("Parent scope is not a valid scope")
            __curr_scope = parent_scope

            continue
        return True

    raise ParseError(
        f"Variable \"{var_token}\" is not defined within its scope"
    )


def parse(input_tokens: list[Token]) -> list[Token] | None:
    init_global_scope()
    curr_scope: ScopeType = scope

    output_tokens = []

    NULL_SCOPE_STR = ""
    dest_scope_name = NULL_SCOPE_STR
    line_tokens = []
    for tok_idx, token in enumerate(input_tokens):
        try:
            match token:
                # Function declaration
                case FunctionDeclaration():
                    func_decl_dict[token.name] = token
                    register_new_scope(
                        curr_scope,
                        SCOPE_KEY_PREFIX__FUNC + token.name,
                        token.arg_list
                    )
                case Function():
                    func_dict[token.name] = token
                    if token.name in func_decl_dict:
                        del func_decl_dict[token.name]
                    
                    func_name = SCOPE_KEY_PREFIX__FUNC + token.name
                    register_new_scope(curr_scope, func_name, token.arg_list)
                    dest_scope_name = func_name

                    output_tokens.append(token)

                # Scopes
                case ScopeStart():
                    # For the if condition case
                    if line_tokens:
                        output_tokens.extend(
                            convert_to_rpn(curr_scope, line_tokens)
                        )

                    if dest_scope_name not in curr_scope:
                        if dest_scope_name == NULL_SCOPE_STR:
                            raise ParseError("Destination scope not found")

                        raise ParseError(
                            f"\"{dest_scope_name}\" not in the current scope"
                        )
                    value = curr_scope[dest_scope_name]
                    if not isinstance(value, OrderedDict):
                        raise ParseError(
                            f"\"{dest_scope_name}\" is not a scope"
                        )
                    curr_scope = value
                    output_tokens.append(token)
                    dest_scope_name = NULL_SCOPE_STR

                case ScopeEnd():
                    if SCOPE_RETURN_KEY not in curr_scope:
                        raise ParseError(
                            "Cannot go beyond the global scope"
                        )
                    value = curr_scope[SCOPE_RETURN_KEY]
                    if not isinstance(value, OrderedDict):
                        raise ParseError(
                            f"\"{dest_scope_name}\" is not a scope"
                        )
                    curr_scope = value
                    output_tokens.append(token)
                
                # Branching statements
                case If() | Loop():
                    if isinstance(token, If):
                        branch_name = SCOPE_KEY_PREFIX__IF
                    else:
                        branch_name = SCOPE_KEY_PREFIX__LOOP

                    name_count = 0
                    while (branch_name + f"{name_count}") in curr_scope:
                        name_count += 1

                    branch_name += f"{name_count}"

                    register_new_scope(curr_scope, branch_name)
                    output_tokens.append(token)
                    dest_scope_name = branch_name

                case Return() | LoopContinue() | LoopBreak() | Else():
                    output_tokens.append(token)

                # Variable
                case Variable():
                    curr_scope[token.name] = token

                # End of line
                case EndOfLine():
                    output_tokens.extend(
                        convert_to_rpn(curr_scope, line_tokens)
                    )
                    if line_tokens:
                        output_tokens.append(token)
                    line_tokens = []

                case _:
                    line_tokens.append(token)

        except ParseError as e:
            e.args = (f"[Token #{tok_idx}] " + "".join(e.args), )
            raise e

    update_func_local_vars()
    return output_tokens


OperatorStack = list[     AbstractOperator
                        | FunctionCall
                        | ExprGroupDelimLeft
                        | ArgBracketLeft
                        | ArrayDelimLeft
                        | ArraySubscriptDelimLeft
                    ]

def convert_to_rpn(curr_scope: OrderedDict, token_list: list[Token]) \
        -> list[Token]:
    """
    Convert a sequence of tokens to its equivalent sequence in RPN.
    This is an implementation of the Shunting Yard algorithm.
    """
    operator_stack: OperatorStack = []
    output_queue = []

    for token in token_list:
        match token:
            case (      Integer()
                      | Float()
                      | VariableInvoke()
                      | Variable()
            ):
                if (        isinstance(token, VariableInvoke)
                    and not var_in_scope(curr_scope, token) ):
                    raise ParseError(
                        f"Variable \"{token.name}\" is not defined"
                    )
                output_queue.append(token)

            case (    LeftUnaryOp()
                    | RightUnaryOp()
                    | BinaryOp()
                    | TypeCastOp()
                    | AssignOp()
                    | MemberAccessOp()
                    | FunctionCall()
            ):
                if (    isinstance(token, FunctionCall)
                    and token.func_name not in func_dict ):
                        raise ParseError(
                            f"Function \"{token.func_name}\" is not defined"
                        )

                while operator_stack:
                    op_token = operator_stack[-1]

                    if (not isinstance(op_token, AbstractOperator)):
                        break

                    if op_token.order > token.order:
                        output_queue.append( operator_stack.pop() )
                        continue
                    break
                operator_stack.append(token)

            case (    ExprGroupDelimLeft()
                    | ArgBracketLeft()
                    | ArrayDelimLeft()
                    | ArraySubscriptDelimLeft()
            ):
                operator_stack.append(token)

            case (      ExprGroupDelimRight()
                      | ArgBracketRight()
                      | ArrayDelimRight()
                      | ArraySubscriptDelimRight()
            ):
                while operator_stack:
                    op_token = operator_stack[-1]
                    if (not isinstance(op_token, AbstractOperator)) :
                        if isinstance(op_token, ArraySubscriptDelimLeft):
                            output_queue.append(BinaryOp(OP_ARR_SUBSCR))

                        # Discard the left bracket
                        operator_stack.pop()
                        break

                    output_queue.append( operator_stack.pop() )
                else:
                    raise ParseError("Imbalanced left bracket")

            case ArgDelim() | ArrayMemberDelim():
                while operator_stack:
                    op_token = operator_stack[-1]
                    if (   isinstance(op_token, ArgBracketLeft)
                        or isinstance(op_token, ArrayDelimLeft) ):
                            break
                    output_queue.append( operator_stack.pop() )
                else:
                    raise ParseError("Missing left bracket")
                output_queue.append(token)

            case _:
                raise ParseError(
                    f"Invalid token encountered in converting to "
                    f"RPN expression: \"{token.__class__.__name__}\""
                )
    while operator_stack:
        output_queue.append( operator_stack.pop() )
    return output_queue


def update_func_local_vars():
    for func_name, func_obj in func_dict.items():
        local_var_list: list[Variable] = []
        func_scope = scope[SCOPE_KEY_PREFIX__FUNC + func_name]
        if isinstance(func_scope, Variable):
            raise ParseError("Expected a scope object, got variable")

        local_scope_list: list[ScopeType] = [func_scope]
        while local_scope_list:
            curr_scope = local_scope_list.pop()
            for name, value in curr_scope.items():
                if name == SCOPE_RETURN_KEY:
                    continue

                match value:
                    case Variable():
                        local_var_list.append(value)
                    case OrderedDict():
                        local_scope_list.append(value)
                    case _:
                        raise ParseError("Invalid scope element")

        func_obj.update(local_var=local_var_list)