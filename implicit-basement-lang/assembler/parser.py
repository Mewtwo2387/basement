from .token.array_elem  import (ArraySubscriptDelimLeft,
                                ArraySubscriptDelimRight)
from .token.block       import  Block, BlockScopeEnd
from .token.branch      import (If,
                                ElseIf,
                                Else,
                                Loop,
                                LoopBreak,
                                LoopContinue,
                                ConditionScopeEnd,
                                LoopScopeEnd)
from .token.delim       import (ExprGroupDelimLeft,
                                ExprGroupDelimRight,
                                EndOfLine)
from .token.function    import (Function,
                                FunctionDeclaration,
                                FunctionScopeEnd,
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
                             MemberAccessOp,
                             FunctionCall,
                             OP_ARR_SUBS)
from .token.scope_elem   import ScopeStart, ScopeEnd
from .token.token        import Token
from .token.variable     import Variable, VariableInvoke, StructMemberInvoke

from .data_type.array       import ArrayType
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
                    func_key = ( curr_scope_key
                               + SCOPE_PREFIX__FUNC
                               + token.name)
                    scope[func_key] = token

                case Function():
                    func_dict[token.name] = token

                    # Once the function is defined, remove any prev declaration.
                    if token.name in func_decl_dict:
                        del func_decl_dict[token.name]

                    # Register this scoping unit to the scope dict.
                    func_key = ( curr_scope_key
                               + SCOPE_PREFIX__FUNC
                               + token.name)
                    scope[func_key] = token
                    # ... and attach the key of this function to the token for
                    # code generation.
                    token.id = func_key

                    # Push the function and scope start token to the output
                    tok_idx += 1
                    scope_start_token = input_tokens[tok_idx]
                    output_tokens.extend((token, scope_start_token))

                    # Go to this scoping unit's scope
                    curr_scope_key = func_key + SCOPE_KEY_DELIM
                    # Also set this function's arguments as variables only
                    # visible within the function's scope.
                    for arg in token.arg_list:
                        scope[curr_scope_key + arg.name] = arg
                
                case Block():
                    # Find and set an unused name for this block token.
                    block_key = curr_scope_key + SCOPE_PREFIX__BLOCK
                    block_idx = 0
                    while f"{block_key}{block_idx}" in scope:
                        block_idx += 1
                    block_key += str(block_idx)

                    # Register this block to the scope, and set the token's id
                    # for code generation.
                    scope[block_key] = token
                    token.id = block_key
                    
                    # Pass this and the scope start token through the output
                    tok_idx += 1
                    scope_start_token = input_tokens[tok_idx]
                    output_tokens.extend((token, scope_start_token))

                    # Go to the scoping block's scope
                    curr_scope_key = block_key + SCOPE_KEY_DELIM
                
                # Branching statements
                case If() | ElseIf() | Else() | Loop() :
                    branch_key = curr_scope_key
                    match token:
                        case If():
                            branch_key += SCOPE_PREFIX__IF
                        case ElseIf():
                            branch_key += SCOPE_PREFIX__ELIF
                        case Else():
                            branch_key += SCOPE_PREFIX__ELSE
                        case _:
                            branch_key += SCOPE_PREFIX__LOOP

                    # Find and set a name for this branching statement token
                    branch_idx = 0
                    while f"{branch_key}{branch_idx}" in scope:
                        name_count += 1
                    branch_key += str(branch_idx)

                    # Register this branching statement to the scope
                    scope[branch_key] = token
                    # ... and set the token's id for code generation.
                    token.id = branch_key

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
                    curr_scope_key = branch_key + SCOPE_KEY_DELIM

                case (  ScopeEnd()
                      | FunctionScopeEnd()
                      | BlockScopeEnd()
                      | ConditionScopeEnd()
                      | LoopScopeEnd() ):
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

                    # Push the return expression to the output
                    # NOTE: The EOL token is not needed anymore since the
                    #       return is already a statement.
                    if ret_expr_tokens:
                        output_tokens.extend(
                                convert_to_rpn(ret_expr_tokens, struct_list)
                            )
                    output_tokens.append(token)

                case Variable():
                    # Register this variable declaration to the scope
                    var_key = curr_scope_key + token.name
                    scope[var_key] = token
                    # ... and set the token's id for code generation.
                    token.id = var_key

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

    tok_idx = 0
    while tok_idx < len(token_list):
        token = token_list[tok_idx]
        match token:
            case ( Integer()
                 | Float()
                 | VariableInvoke()
                 | StructMemberInvoke() ):

                if isinstance(token, VariableInvoke):
                    var_token = get_matching_var_token(token)
                    if not var_token:
                        raise ParseError(
                            f"Variable \"{token.name}\" is not defined or "
                             "visible within the scope the variable is invoked"
                        )
                    token.var = var_token

                elif isinstance(token, StructMemberInvoke):
                    matching_structs = get_matching_structs(token, struct_list)
                    if not matching_structs:
                        raise ParseError(
                            f"\"{token.name}\" is not a member of any struct"
                        )
                    
                    # Find the struct of the corresponding variable invoke token
                    struct = get_struct_of_matching_var(token,
                                                        token_list,
                                                        tok_idx)
                    token.struct = struct

                output_queue.append(token)

            case ( LeftUnaryOp()
                 | RightUnaryOp()
                 | BinaryOp()
                 | TypeCastOp()
                 | AssignOp()
                 | MemberAccessOp()
                 | FunctionCall() ):

                if (    isinstance(token, FunctionCall)
                    and token.func_name not in func_dict ):
                        raise ParseError(
                            f"Function \"{token.func_name}\" is not defined"
                        )

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
                init_tokens, tok_idx = res
                output_queue.extend( init_tokens )
            case InitDelimRight():
                raise ParseError("Misplaced right initializer delimiter")
            case InitMemberDelim():
                raise ParseError("Misplaced initializer member delimiter")

            case ( ExprGroupDelimLeft()
                 | ArgBracketLeft()
                 | ArraySubscriptDelimLeft() ):
                operator_stack.append(token)

            case ( ExprGroupDelimRight()
                 | ArgBracketRight()
                 | ArraySubscriptDelimRight() ):
                while operator_stack:
                    op_token = operator_stack[-1]
                    if (not isinstance(op_token, Operator)):
                        if isinstance(op_token, ArraySubscriptDelimLeft):
                            output_queue.append(BinaryOp(OP_ARR_SUBS))

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


def get_matching_var_token(token: VariableInvoke) -> Variable | None:
    __curr_scope_key = curr_scope_key

    while True:
        var_token_key = __curr_scope_key + token.name
        if var_token_key in scope:
            break
        if len(__curr_scope_key) == 0:
            return None
        __curr_scope_key = go_up_one_scope(__curr_scope_key)
    
    var_token = scope.get(var_token_key)
    if not var_token:
        raise ParseError(
            f"Variable \"{token.name}\" is supposedly defined within the scope "
            f"\"{__curr_scope_key}\", but the corresponding variable "
             "declaration token cannot be found"
        )
    if not isinstance(var_token, Variable):
        raise ParseError(
            f"Variable \"{token.name}\" exists but its corresponding variable"
             " declaration token is not the correct type.\n"
            f"Found the following token instead: {var_token}"
        )

    return var_token


def get_matching_structs(
            mmb_token: StructMemberInvoke,
            structs: list[StructDecl]
        ) -> list[StructDecl]:
    matched_structs = []

    for s in structs:
        if mmb_token.name in s.members:
            matched_structs.append(s)

    return matched_structs


def get_struct_of_matching_var(
            mmb_token:  StructMemberInvoke,
            token_list: list[Token],
            tok_idx:    int
        ) -> StructDecl:

    if tok_idx < 2:
        raise ParseError(
             "No more associated variable invoke token to search for for "
            f" \"{mmb_token.name}\""
        )
    if not isinstance(token_list[tok_idx - 1], MemberAccessOp):
        raise ParseError(
             "Unexpected token before the struct member token. "
            f"Must be a member access operator."
        )

    # Search for the variable invoke corresponding to this member token.
    bracket_lvl = 0
    peek_idx = tok_idx - 2
    peek_token = token_list[peek_idx]
    while peek_idx >= 0:
        if isinstance(peek_token,
                      (ArraySubscriptDelimRight, ExprGroupDelimRight)):
            bracket_lvl += 1

        if bracket_lvl == 0:
            break

        if isinstance(peek_token,
                      (ArraySubscriptDelimLeft, ExprGroupDelimLeft)):
            bracket_lvl -= 1

        peek_idx -= 1
        peek_token = token_list[peek_idx]
    
    if bracket_lvl > 0 or peek_idx < 0:
        raise ParseError(
             "No token associated to the struct member token "
            f"\"{mmb_token.name}\""
        )
    
    if not isinstance(peek_token, VariableInvoke):
        raise ParseError(
             "Expected a variable token to associate with the struct member "
            f"\"{mmb_token.name}\". The following type is found instead: "
            f"{type(peek_token).__name__}"
        )

    if peek_token.var is None:
        raise ParseError(
            f"Type of variable \"{peek_token.name}\" is unknown. "
            f"Cannot verify the struct member \"{mmb_token.name}\""
        )
    
    struct_type = peek_token.var.data_type

    if isinstance(struct_type, ArrayType):
        struct_type = struct_type.mmb_type

    if not isinstance(struct_type, StructDecl):
        raise ParseError(
            f"Type of variable \"{peek_token.name}\" is not a struct. "
            f"Struct member \"{mmb_token.name}\" cannot be its member"
        )
    if mmb_token.name not in struct_type.members:
        raise ParseError(
            f"\"{mmb_token.name}\" is not a member of the struct"
            f" \"{peek_token.var.name}\""
        )
    
    return struct_type


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
