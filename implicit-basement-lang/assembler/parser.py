from .token.array_elem  import (ArraySubscriptDelimLeft,
                                ArraySubscriptDelimRight)
from .token.block       import  Block
from .token.branch      import  If, ElseIf, Else, Loop, LoopBreak, LoopContinue
from .token.delim       import (ExprGroupDelimLeft,
                                ExprGroupDelimRight,
                                EndOfLine)
from .token.function    import (Function,
                                FunctionDeclaration,
                                ArgBracketLeft,
                                ArgBracketRight,
                                ArgDelim,
                                Return)
from .token.initializer import (InitDelimLeft,
                                InitDelimRight,
                                InitMemberDelim)
from .token.number   import Integer, Float
from .token.operator import (Operator,
                             LeftUnaryOp,
                             RightUnaryOp,
                             BinaryOp,
                             TypeCastOp,
                             AssignOp,
                             FieldAccessOp,
                             FunctionCall,
                             OP_ARR_SUBSCR)
from .token.scope_elem   import ScopeStart, ScopeEnd
from .token.token        import Token
from .token.variable     import Variable, VariableInvoke

from .data_type.struct_decl import StructDecl

from .error import ParseError


scope: dict[str, Token] = {}
curr_scope_key = ""    # NOTE: Empty string means we are in the root scope.

SCOPE_PREFIX__FUNC  = "func_"
SCOPE_PREFIX__IF    = "if_"
SCOPE_PREFIX__ELIF  = "elseif_"
SCOPE_PREFIX__ELSE  = "else_"
SCOPE_PREFIX__LOOP  = "loop_"
SCOPE_PREFIX__BLOCK = "block"
SCOPE_KEY_DELIM = "/"

func_dict: dict[str, Function] = {}
func_decl_dict: dict[str, FunctionDeclaration] = {}


def parse(
            input_tokens: list[Token],
            struct_list: list[StructDecl]
        ) -> tuple[list[Token], dict[str, Token]]:
    global curr_scope_key

    output_tokens = []
    line_tokens = []

    tok_idx = 0
    while tok_idx < len(input_tokens):
        token = input_tokens[tok_idx]
        try:
            match token:
                case FunctionDeclaration():
                    func_decl_dict[token.name] = token
                    func_name = ( curr_scope_key
                                + SCOPE_PREFIX__FUNC
                                + token.name)
                    scope[func_name] = token

                case Function():
                    func_dict[token.name] = token

                    # Once the function is defined, remove any prev declaration.
                    if token.name in func_decl_dict:
                        del func_decl_dict[token.name]

                    # Register this scoping unit to the scope dict.
                    func_name = ( curr_scope_key
                                + SCOPE_PREFIX__FUNC
                                + token.name)
                    scope[func_name] = token

                    # Push the function and scope start token to the output
                    tok_idx += 1
                    scope_start_token = input_tokens[tok_idx]
                    output_tokens.extend((token, scope_start_token))

                    # Go to this scoping unit's scope
                    curr_scope_key = func_name + SCOPE_KEY_DELIM
                    # Also set this function's arguments as variables only
                    # visible within the function's scope.
                    for arg in token.arg_list:
                        scope[curr_scope_key + arg.name] = arg
                
                case Block():
                    # Find and set an unused name for this block token.
                    block_name = curr_scope_key + SCOPE_PREFIX__BLOCK
                    block_idx = 0
                    while f"{block_name}{block_idx}" in scope:
                        block_idx += 1
                    block_name += str(block_idx)

                    scope[block_name] = token
                    
                    # Pass this and the scope start token through the output
                    tok_idx += 1
                    scope_start_token = input_tokens[tok_idx]
                    output_tokens.extend((token, scope_start_token))

                    # Go to the scoping block's scope
                    curr_scope_key = block_name + SCOPE_KEY_DELIM
                
                # Branching statements
                case If() | ElseIf() | Else() | Loop() :
                    branch_name = curr_scope_key
                    match token:
                        case If():
                            branch_name += SCOPE_PREFIX__IF
                        case ElseIf():
                            branch_name += SCOPE_PREFIX__ELIF
                        case Else():
                            branch_name += SCOPE_PREFIX__ELSE
                        case _:
                            branch_name += SCOPE_PREFIX__LOOP

                    # Find and set a name for this branching statement token
                    branch_idx = 0
                    while f"{branch_name}{branch_idx}" in scope:
                        name_count += 1
                    branch_name += str(branch_idx)

                    scope[branch_name] = token

                    # Collect the condition expr tokens.
                    cond_tokens: list[Token] = []
                    tok_idx += 1
                    while not isinstance(input_tokens[tok_idx], ScopeStart):
                        cond_tokens.append(input_tokens[tok_idx])
                        tok_idx += 1
                    scope_start_token = input_tokens[tok_idx]

                    # Push the condition expr in RPN to the output list.
                    if cond_tokens:
                        output_tokens.extend(
                                convert_to_rpn(cond_tokens, struct_list)
                            )

                    # Pass this and the scope start token through the output
                    output_tokens.extend((token, scope_start_token))

                    # Go to the scoping block's scope
                    curr_scope_key = branch_name + SCOPE_KEY_DELIM

                case ScopeEnd():
                    output_tokens.append(token)
                    curr_scope_key = go_up_one_scope(curr_scope_key)

                case LoopContinue() | LoopBreak():
                    output_tokens.append(token)
                
                # NOTE: This is a statement, i.e. no expr tokens should precede
                #       it. Only other statement tokens, e.g. IF, EOL
                case Return():
                    # Collect the return expression
                    ret_expr_tokens: list[Token] = []
                    tok_idx += 1
                    while not isinstance(input_tokens[tok_idx], EndOfLine):
                        ret_expr_tokens.append(input_tokens[tok_idx])
                        tok_idx += 1
                    eol_token = input_tokens[tok_idx]
                    
                    # Push the return expression to the output
                    # before return token and the EOL
                    if ret_expr_tokens:
                        output_tokens.extend(
                                convert_to_rpn(ret_expr_tokens, struct_list)
                            )
                    output_tokens.extend([token, eol_token])

                case Variable():
                    scope[curr_scope_key + token.name] = token

                    # If we are in a (non-root) scope, we must be in a function.
                    # Update the current function's local variables
                    if len(curr_scope_key) > 0:
                        func_token = get_curr_func()
                        if func_token is None:
                            raise ParseError(
                                 "Failed to get the function for the "
                                f"local variable \"{token.name}\""
                            )
                        func_token.update(local_var=token)

                # End of line
                case EndOfLine():
                    output_tokens.extend(
                        convert_to_rpn(line_tokens, struct_list)
                    )
                    # If the line is empty anyways, don't bother putting an
                    # EOL token to the output list.
                    if line_tokens:
                        output_tokens.append(token)
                    line_tokens = []

                case _:
                    line_tokens.append(token)

        except ParseError as e:
            e.args = (f"[Parser @ token#{tok_idx}] " + "".join(e.args), )
            raise e
        
        tok_idx += 1

    return output_tokens, scope.copy()


OperatorStack = list[     Operator
                        | FunctionCall
                        | ExprGroupDelimLeft
                        | ArgBracketLeft
                        | ArraySubscriptDelimLeft
                        | InitDelimLeft
                    ]

def convert_to_rpn(token_list: list[Token], struct_list: list[StructDecl]) \
        -> list[Token]:
    """
    Convert a sequence of tokens to its equivalent sequence in RPN.
    This is an implementation of the Shunting Yard algorithm.
    """
    operator_stack: OperatorStack = []
    output_queue = []

    var_is_struct_mmb = False

    tok_idx = 0
    while tok_idx < len(token_list):
        token = token_list[tok_idx]
        match token:
            case ( Integer()
                 | Float()
                 | VariableInvoke() ):

                if (        isinstance(token, VariableInvoke)
                        and not var_is_struct_mmb):
                    if not is_var_in_scope(token):
                        raise ParseError(
                            f"Variable \"{token.name}\" is not defined"
                        )
                var_is_struct_mmb = False
                output_queue.append(token)

            case ( LeftUnaryOp()
                 | RightUnaryOp()
                 | BinaryOp()
                 | TypeCastOp()
                 | AssignOp()
                 | FieldAccessOp()
                 | FunctionCall() ):

                if (    isinstance(token, FunctionCall)
                    and token.func_name not in func_dict ):
                        raise ParseError(
                            f"Function \"{token.func_name}\" is not defined"
                        )
                
                # For the struct member access operator
                var_is_struct_mmb = next_tok_is_struct_mmb(token_list,
                                                           tok_idx,
                                                           struct_list)

                while operator_stack:
                    op_token = operator_stack[-1]

                    if (not isinstance(op_token, Operator)):
                        break

                    if op_token.order > token.order:
                        output_queue.append( operator_stack.pop() )
                        continue
                    break
                operator_stack.append(token)

            case InitDelimLeft():
                tok_idx += 1   # Proceed to the struct init
                res = build_initializer(struct_list,
                                        token_list,
                                        tok_idx)
                struct_init_tokens, tok_idx = res
                output_queue.extend( struct_init_tokens )
            case InitDelimRight():
                raise ParseError("Misplaced right initializer delimiter")
            case InitMemberDelim():
                raise ParseError("Misplaced initializer member delimiter")

            case (    ExprGroupDelimLeft()
                    | ArgBracketLeft()
                    | ArraySubscriptDelimLeft()
            ):
                operator_stack.append(token)

            case (      ExprGroupDelimRight()
                      | ArgBracketRight()
                      | ArraySubscriptDelimRight()
            ):
                while operator_stack:
                    op_token = operator_stack[-1]
                    if (not isinstance(op_token, Operator)):
                        if isinstance(op_token, ArraySubscriptDelimLeft):
                            output_queue.append(BinaryOp(OP_ARR_SUBSCR))

                        # Discard the left bracket
                        operator_stack.pop()
                        break

                    output_queue.append( operator_stack.pop() )
                else:
                    raise ParseError("Imbalanced left bracket")

            case ArgDelim():
                while operator_stack:
                    op_token = operator_stack[-1]
                    if isinstance(op_token, ArgBracketLeft):
                        break
                    output_queue.append( operator_stack.pop() )
                else:
                    raise ParseError("Missing left bracket")
                if not isinstance(token, ArgDelim):
                    output_queue.append(token)

            case _:
                raise ParseError(
                    f"Invalid token encountered in converting to "
                    f"RPN expression: \"{token.__class__.__name__}\""
                )

        tok_idx += 1
    
    while operator_stack:
        output_queue.append( operator_stack.pop() )
    return output_queue


def get_curr_func() -> Function | None:
    if len(curr_scope_key) == 0:
        return None

    # Ignore the final char which should be the scope key delimiter
    scope_key_elems = curr_scope_key[:-1].split(SCOPE_KEY_DELIM)
    scope_key_elems.reverse()

    func_name: str
    for i, elem in enumerate(scope_key_elems):
        if elem.find(SCOPE_PREFIX__FUNC) != -1 :
            func_name_elems = scope_key_elems[i:]
            func_name_elems.reverse()
            func_name = SCOPE_KEY_DELIM.join(func_name_elems)
            break
    else:
        return None
    
    func_token = scope.get(func_name)
    if isinstance(func_token, Function):
        return func_token
    elif func_token is None:
        raise ParseError(
            f"Function name \"{func_name}\" exists but is not registered"
        )
    
    raise ParseError(
         "The following token is not a function but registered as one:  "
        f"{func_token}"
    )


def go_up_one_scope(scope_key: str) -> str:
    """
    Pop off the substring representing the current scope as delimited by the
    scope string delimiter.
    """
    try:
        next_final_idx = scope_key.rindex(SCOPE_KEY_DELIM, 0, -2)
    except ValueError:
        # NOTE: Will raise an exception once we are at the
        #       "root" scope.
        next_final_idx = 0

    if next_final_idx == 0:
        return ""   # Root scope
    return scope_key[:next_final_idx] + SCOPE_KEY_DELIM


def is_var_in_scope(token: VariableInvoke) -> bool:
    __curr_scope_key = curr_scope_key

    while True:
        token_name = __curr_scope_key + token.name
        if token_name in scope:
            return True
        if len(__curr_scope_key) == 0:
            break
        __curr_scope_key = go_up_one_scope(__curr_scope_key)
    
    return False


def is_struct_mmb_defined(
            mmb_token: VariableInvoke,
            structs:   list[StructDecl]
        ) -> bool:
    
    all_mmbs = {s.name: {mmb for mmb in s.members} for s in structs}
    mmb_in_structs = [
        mmb_token.name in f_set for f_set in all_mmbs.values()
    ]
    return any(mmb_in_structs)


def next_tok_is_struct_mmb(token_list:  list[Token],
                             tok_idx:     int,
                             struct_list: list[StructDecl]) -> bool:

    if not isinstance(token_list[tok_idx], FieldAccessOp):
        return False
    
    if tok_idx >= len(token_list):
        raise ParseError("Expected a struct member")
    
    mmb_token = token_list[tok_idx + 1]   # Peek at the next token
    if not isinstance(mmb_token, VariableInvoke):
        raise ParseError(
            "Expects a name struct member name for the struct member access"
            " operator."
        ) 
    if not is_struct_mmb_defined(mmb_token, struct_list):
        raise ParseError(
            f"The name '{mmb_token.name}' is not a member of any struct."
        )

    return True


def build_initializer(
            struct_list: list[StructDecl],
            token_list:  list[Token],
            tok_idx:     int
        ) -> tuple[list[Token], int]:

    init_expr_end_types = (InitDelimRight, InitMemberDelim)

    _tok_idx = tok_idx
    nesting_lvl = 1

    output_tokens      : list[Token] = []
    init_mmb_token_list: list[Token] = []

    while _tok_idx < len(token_list):
        token = token_list[_tok_idx]
        _tok_idx += 1

        if isinstance(token, InitDelimLeft):
            nesting_lvl += 1
        if isinstance(token, init_expr_end_types):
            nesting_lvl -= 1

        if nesting_lvl == 0:
            # Convert the initializer member expr into RPN.
            output_tokens.extend(
                    convert_to_rpn(init_mmb_token_list, struct_list)
                )

            # If the right delimiter is reached, the parsing ends
            if isinstance(token, InitDelimRight):
                _tok_idx += 1  # Skip the right delimiter
                break

            # But if an init member delimeter (the comma) is reached,
            # Reset the nesting level to parse the next expression
            nesting_lvl += 1  
            init_mmb_token_list = []
            continue

        init_mmb_token_list.append(token)

    return output_tokens, _tok_idx


def calc_expr_token_size(token_list: list[Token]) -> int:
    size = 0    
    for token in token_list:
        if isinstance(token, TypeCastOp):
            curr_size = token.to_type.size
        else:
            curr_size = token.size

        if curr_size > size:
            size = curr_size
    return size
