import opcodes as op
import data_size
from data_size import WORD_SIZE
from function import Function

from typing import Dict, List


FILLER_BYTE_ARR = [0 for _ in range(WORD_SIZE - 1)]


def int_to_bytes(n, size):
    return [(n >> (s * 8)) & 0xFF for s in range(size)]


def load_dummy_bytes(name: str):
    return [name, *FILLER_BYTE_ARR]


def write_func_table_segment(
        bytecode       : List[int],
        func_name_dict : Dict[str, str],
        func_table     : Dict[str, Function],
        address_table  : Dict[str, int]
    ):

    for func_name, func_tbl_name in func_name_dict.items():
        # Register the address of the function structure.
        address_table[func_tbl_name] = len(bytecode)
        
        # Push the number of function arguments
        bytecode.extend(
            int_to_bytes(func_table[func_name].arg_num, WORD_SIZE)
        )
        # Push the size of the local variable section of the function in bytes
        bytecode.extend(
            int_to_bytes(func_table[func_name].var_sec_size, WORD_SIZE)
        )
        # Push the size of the address of the function code
        bytecode.extend(
            int_to_bytes(func_table[func_name].address, WORD_SIZE)
        )


def update_label_addr(bytecode: List[int], address_table: Dict[str, int]):
    for i, elem in enumerate(bytecode):
        if isinstance(elem, str):
            bytecode[i : i + WORD_SIZE] = \
                int_to_bytes(address_table[elem], WORD_SIZE)


def write_hello_word_asm():
    """
    Attempt to generate bytecodes  for the following pseudocode:
        int32_t print(int8_t *str) {
            while (*str) {
                putc(*str);
                ++str;
            }
            return 0;
        }

        int32_t main() {
            print("Hello, World!\n");
            return 0;
        }
    """
    bytecode = []

    FTBL_MAIN             = "ftbl__main"
    FTBL_PRINT            = "ftbl__print"
    FUNC_PRINT            = "print"
    FUNC_PRINT__LOOP1     = "loop1"
    FUNC_PRINT__ARG_STR   = "arg_str"
    FUNC_PRINT__END_LOOP1 = "end_loop"
    FUNC_MAIN             = "main"
    FUNC_MAIN__PTR_STR    = "str_ptr"

    address_table = {
        FUNC_PRINT            : -1,
        FUNC_PRINT__LOOP1     : -1,
        FUNC_PRINT__ARG_STR   : -1,
        FUNC_PRINT__END_LOOP1 : -1,
        FUNC_MAIN             : -1,
        FUNC_MAIN__PTR_STR    : -1,
        FTBL_MAIN             : -1,
        FTBL_PRINT            : -1
    }

    func_table = {
        FUNC_PRINT : Function(1, 0, -1),
        FUNC_MAIN  : Function(0, 0, -1)
    }

    func_name_dict = {
        FUNC_PRINT : FTBL_PRINT,
        FUNC_MAIN  : FTBL_MAIN
    }

    ### === CODE SEGMENT === ###

    ### Driver code ###
    bytecode.append(op.CALL)
    bytecode.extend(load_dummy_bytes(FTBL_MAIN))
    bytecode.append(op.DONE)

    ### Function: print ###
    # Update the `FUNC_PRINT` address
    address_table[FUNC_PRINT] = len(bytecode)
    func_table[FUNC_PRINT].address = address_table[FUNC_PRINT]
    # Update the address of the label `LOOP1`
    address_table[FUNC_PRINT__LOOP1] = len(bytecode)
    # Update the relative address OFFSET_STR (relative to the return address)
    address_table[FUNC_PRINT__ARG_STR] = \
        func_table[FUNC_PRINT].call_frame_size

    # While loop condition
    bytecode.append(op.LOAD64_OFF_FP)
    bytecode.extend(load_dummy_bytes(FUNC_PRINT__ARG_STR))

    bytecode.append(op.LOAD8)

    bytecode.append(op.JMPZ_ADDR)
    bytecode.extend(load_dummy_bytes(FUNC_PRINT__END_LOOP1))


    # Print one character at a time
    bytecode.append(op.LOAD64_OFF_FP)
    bytecode.extend(load_dummy_bytes(FUNC_PRINT__ARG_STR))

    bytecode.append(op.LOAD8)

    bytecode.append(op.OUT_CHAR)

    # Go to the next character in the string.
    bytecode.append(op.LOAD64_OFF_FP)
    bytecode.extend(load_dummy_bytes(FUNC_PRINT__ARG_STR))

    bytecode.append(op.ADD_CONST)
    bytecode.extend(int_to_bytes(data_size.INT8_SIZE, WORD_SIZE))

    bytecode.append(op.STORE64_OFF_FP)
    bytecode.extend(load_dummy_bytes(FUNC_PRINT__ARG_STR))

    bytecode.append(op.JUMP_ADDR)
    bytecode.extend(load_dummy_bytes(FUNC_PRINT__LOOP1))

    # Update the `END_LOOP1` address
    address_table[FUNC_PRINT__END_LOOP1] = len(bytecode)

    bytecode.append(op.LOAD32_CONST)
    bytecode.extend(int_to_bytes(0, WORD_SIZE))

    bytecode.append(op.RETURN)

    ### Function: main ###
    # Update the `FUNC_MAIN` address
    address_table[FUNC_MAIN] = len(bytecode)
    func_table[FUNC_MAIN].address = address_table[FUNC_MAIN]

    bytecode.append(op.LOAD64_CONST)
    bytecode.extend(load_dummy_bytes(FUNC_MAIN__PTR_STR))

    bytecode.append(op.CALL)
    bytecode.extend(load_dummy_bytes(FTBL_PRINT))

    bytecode.append(op.LOAD32_CONST)
    bytecode.extend(int_to_bytes(0, WORD_SIZE))

    bytecode.append(op.RETURN)

    ### === CONSTANT SEGMENT === ###
    # Update the `STR_PTR` address
    address_table[FUNC_MAIN__PTR_STR] = len(bytecode)

    string = "Hello, World!\n\0"
    bytecode.extend([ord(c) for c in string])

    ### === FUNCTION STRUCTURE SEGMENT === ###
    write_func_table_segment(
        bytecode, func_name_dict, func_table, address_table
    )

    update_label_addr(bytecode, address_table)
    
    return bytecode


def write_hello_word_optimized_asm():
    bytecode = []

    FTBL_MAIN              = "ftbl__main"
    FTBL_PRINT             = "ftbl__print"
    FUNC_PRINT             = "print"
    FUNC_PRINT__LOOP1      = "loop1"
    FUNC_PRINT__ARG_STR    = "arg_str"
    FUNC_PRINT__END_LOOP1  = "end_loop"
    FUNC_MAIN              = "main"
    FUNC_MAIN__PTR_STR     = "str_ptr"

    address_table = {
        FUNC_PRINT             : -1,
        FUNC_PRINT__LOOP1      : -1,
        FUNC_PRINT__ARG_STR    : -1,
        FUNC_PRINT__END_LOOP1  : -1,
        FUNC_MAIN              : -1,
        FUNC_MAIN__PTR_STR     : -1,
        FTBL_MAIN              : -1,
        FTBL_PRINT             : -1
    }

    func_table = {
        FUNC_PRINT : Function(1, 0, -1),
        FUNC_MAIN  : Function(0, 0, -1)
    }

    func_name_dict = {
        FUNC_PRINT : FTBL_PRINT,
        FUNC_MAIN  : FTBL_MAIN
    }

    ## === CODE SEGMENT === ##
    ## Driver code ##
    bytecode.append(op.CALL)
    bytecode.extend(load_dummy_bytes(FTBL_MAIN))

    bytecode.append(op.DONE)

    ## Function `print` ##
    # Register the address of FUNC_PRINT
    address_table[FUNC_PRINT] = len(bytecode)
    func_table[FUNC_PRINT].address = address_table[FUNC_PRINT]
    # Update the address OFFSET_STR relative to the return address
    #   In this case, the argument is the very first element of the call frame.
    address_table[FUNC_PRINT__ARG_STR] = \
        func_table[FUNC_PRINT].call_frame_size

    bytecode.append(op.LOAD64_OFF_FP)
    bytecode.extend(load_dummy_bytes(FUNC_PRINT__ARG_STR))

    # Register the address of LOOP1
    address_table[FUNC_PRINT__LOOP1] = len(bytecode)

    bytecode.append(op.DUP)

    bytecode.append(op.LOAD8)

    bytecode.append(op.JMPZ_ADDR)
    bytecode.extend(load_dummy_bytes(FUNC_PRINT__END_LOOP1))

    bytecode.append(op.DUP)

    bytecode.append(op.LOAD8)

    bytecode.append(op.OUT_CHAR)

    bytecode.append(op.ADD_CONST)
    bytecode.extend(int_to_bytes(data_size.INT8_SIZE, WORD_SIZE))

    bytecode.append(op.JUMP_ADDR)
    bytecode.extend(load_dummy_bytes(FUNC_PRINT__LOOP1))

    # Register the address of END_LOOP1
    address_table[FUNC_PRINT__END_LOOP1] = len(bytecode)

    bytecode.append(op.RETURN)

    ## Function `main` ##
    # Register the address of FUNC_MAIN
    address_table[FUNC_MAIN] = len(bytecode)

    bytecode.append(op.LOAD64_CONST)
    bytecode.extend(load_dummy_bytes(FUNC_MAIN__PTR_STR))

    bytecode.append(op.CALL)
    bytecode.extend(load_dummy_bytes(FTBL_PRINT))

    bytecode.append(op.RETURN)

    ## === CONSTANT SEGMENT === ##
    # Register the address of PTR_STR
    address_table[FUNC_MAIN__PTR_STR] = len(bytecode)
    func_table[FUNC_MAIN].address = address_table[FUNC_MAIN]

    string = "Hello, World!\n\0"
    bytecode.extend([ord(c) for c in string])

    ## === FUNCTION STRUCTURE SEGMENT == ##
    write_func_table_segment(
        bytecode, func_name_dict, func_table, address_table
    )

    # Update the labels
    update_label_addr(bytecode, address_table)
    
    return bytecode


def write_factorial_asm():
    """
    Generate bytecodes for the following pseudocode:s
        int64_t factorial(int32_t n) {
            if (n == 0 | n == 1)
                return 1;
            return factorial(n - 1) * factorial(n - 2);
        }

        int32_t main() {
            int64_t res = factorial(3);
            print(res);
            print("\n");
            return 0;
        }
    """
    bytecode = []

    FTBL_MAIN = "ftbl_main"
    FUNC_MAIN = "main"
    FUNC_MAIN_VAR_RES = "main_res"
    FTBL_FACTORIAL = "ftbl_factorial"
    FUNC_FACTORIAL = "factorial"
    FUNC_FACTORIAL_ARG_N = "factorial_arg_n"
    FUNC_FACTORIAL_ELSE1 = "factorial_else1"

    address_table = {
        FTBL_MAIN            : -1,
        FUNC_MAIN            : -1,
        FUNC_MAIN_VAR_RES    : -1,
        FTBL_FACTORIAL       : -1,
        FUNC_FACTORIAL       : -1,
        FUNC_FACTORIAL_ARG_N : -1,
        FUNC_FACTORIAL_ELSE1 : -1
    }

    func_table = {
        FUNC_MAIN : Function(0, -1, -1),
        FUNC_FACTORIAL : Function(1, -1, -1)
    }

    func_name_dict = {
        FUNC_MAIN : FTBL_MAIN,
        FUNC_FACTORIAL : FTBL_FACTORIAL
    }

    ## === CODE SEGMENT === ##
    ## Driver code ##
    bytecode.append(op.CALL)
    bytecode.extend(
        load_dummy_bytes(FTBL_MAIN)
    )
    
    bytecode.append(op.DONE)

    ## Function `factorial` ##
    # Register the address of the `factorial` function
    address_table[FUNC_FACTORIAL] = len(bytecode)
    func_table[FUNC_FACTORIAL].address = address_table[FUNC_FACTORIAL]
    # Register the size of the local variable section
    #   NOTE: This is automatically generated by the compiler
    func_table[FUNC_FACTORIAL].var_sec_size = 0

    # Register the addresses within the function relative to the return address
    #   Function argument: `n` 
    #       address: At the bottom of the call frame
    address_table[FUNC_FACTORIAL_ARG_N] = \
        func_table[FUNC_FACTORIAL].call_frame_size

    # Assembly code for the following pseudocode expression:
    #   `n == 0 | n == 1`
    # In RPN:
    #   `n, 0, ==, n, 1, ==, | `
    bytecode.append(op.LOAD32_OFF_FP)
    bytecode.extend(
        load_dummy_bytes(FUNC_FACTORIAL_ARG_N)
    )
    bytecode.append(op.LOAD32_CONST)
    bytecode.extend(
        int_to_bytes(0x0, WORD_SIZE)
    )
    bytecode.append(op.EQ)
    bytecode.append(op.LOAD32_OFF_FP)
    bytecode.extend(
        load_dummy_bytes(FUNC_FACTORIAL_ARG_N)
    )
    bytecode.append(op.LOAD32_CONST)
    bytecode.extend(
        int_to_bytes(0x1, WORD_SIZE)
    )
    bytecode.append(op.EQ)
    bytecode.append(op.OR)

    # If TOS is false (i.e. zero), jump to the else clause
    bytecode.append(op.JMPZ_ADDR)
    bytecode.extend( load_dummy_bytes(FUNC_FACTORIAL_ELSE1) )
    # Otherwise, return 1.
    bytecode.append(op.LOAD64_CONST)
    bytecode.extend(
        int_to_bytes(0x1, WORD_SIZE)
    )
    bytecode.append(op.RETURN)

    # Register the address of the label `ELSE1`
    address_table[FUNC_FACTORIAL_ELSE1] = len(bytecode)

    # Assembly code for the following pseudocode expression:
    #   "n * factorial(n - 1)"
    # In RPN:
    #   "n, n, 1, -, factorial, *"
    bytecode.append(op.LOAD32_OFF_FP)
    bytecode.extend( load_dummy_bytes(FUNC_FACTORIAL_ARG_N) )

    bytecode.append(op.DUP)

    bytecode.append(op.LOAD32_CONST)
    bytecode.extend( int_to_bytes(0x1, WORD_SIZE) )

    bytecode.append(op.SUB)

    bytecode.append(op.CALL)
    bytecode.extend( load_dummy_bytes(FTBL_FACTORIAL) )

    bytecode.append(op.MUL)

    bytecode.append(op.RETURN)
    ## End of function `factorial` ##

    ## Function `main` ##
    # Register the address of the function
    address_table[FUNC_MAIN] = len(bytecode)
    func_table[FUNC_MAIN].address = address_table[FUNC_MAIN]

    # Register the size of the local variable section
    #   NOTE: This is automatically generated by the compiler.
    #
    # The function `main` has the following local variable(s):
    #   1. res  (type: int32_t, size: 4 bytes)
    #
    # Total size of the local variable section: 4 bytes.
    func_table[FUNC_MAIN].var_sec_size = 4

    # Register the addresses within the function relative to the return address
    func_main_obj = func_table[FUNC_MAIN]
    address_table[FUNC_MAIN_VAR_RES] = \
        (func_main_obj.call_frame_size
         - (WORD_SIZE - func_main_obj.var_sec_size))
    
    bytecode.append(op.LOAD64_CONST)
    bytecode.extend( int_to_bytes(0x3, WORD_SIZE) )
    bytecode.append(op.CALL)
    bytecode.extend( load_dummy_bytes(FTBL_FACTORIAL) )
    bytecode.append(op.STORE64_OFF_FP)
    bytecode.extend( load_dummy_bytes(FUNC_MAIN_VAR_RES) )

    bytecode.append(op.LOAD64_OFF_FP)
    bytecode.extend( load_dummy_bytes(FUNC_MAIN_VAR_RES) )
    bytecode.append(op.OUT_NUM)

    bytecode.append(op.LOAD8_CONST)
    bytecode.extend( int_to_bytes(ord('\n'), WORD_SIZE) )
    bytecode.append(op.OUT_CHAR)

    bytecode.append(op.LOAD32_CONST)
    bytecode.extend( int_to_bytes(0x0, WORD_SIZE) )
    bytecode.append(op.RETURN)
    ## End of function `main` ##

    ## === GLOBAL CONSTANT SEGMENT === ##
    # (Nothing here)

    ## === FUNCTION TABLE SEGMENT === ##
    write_func_table_segment(
        bytecode, func_name_dict, func_table, address_table
    )

    update_label_addr(bytecode, address_table)
    
    return bytecode