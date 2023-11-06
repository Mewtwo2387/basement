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
        # Update the code address of the function
        func_table[func_name].address = address_table[func_name]
        
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
    # Update the `FUNC_PRINT` and `LOOP1` addresses
    address_table[FUNC_PRINT] = len(bytecode)
    address_table[FUNC_PRINT__LOOP1] = len(bytecode)
    # Update the relative address OFFSET_STR
    address_table[FUNC_PRINT__ARG_STR] = \
        func_table[FUNC_PRINT].call_frame_size

    # While loop condition
    bytecode.append(op.LOAD64_OFF_FP)
    bytecode.extend(load_dummy_bytes(FUNC_PRINT__ARG_STR))

    bytecode.append(op.LOAD8)

    bytecode.append(op.JMPZ_ADDR)
    bytecode.extend(load_dummy_bytes(FUNC_PRINT__END_LOOP1))

    bytecode.append(op.DISCARD)

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

    bytecode.append(op.DISCARD)
    
    bytecode.append(op.LOAD32_CONST)
    bytecode.extend(int_to_bytes(0, WORD_SIZE))

    bytecode.append(op.RETURN)

    ### Function: main ###
    # Update the `FUNC_MAIN` address
    address_table[FUNC_MAIN] = len(bytecode)

    bytecode.append(op.LOAD64_CONST)
    bytecode.extend(load_dummy_bytes(FUNC_MAIN__PTR_STR))

    bytecode.append(op.CALL)
    bytecode.extend(load_dummy_bytes(FTBL_PRINT))

    bytecode.append(op.DISCARD)

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
        FUNC_PRINT__ARG_STR : -1,
        FUNC_PRINT__END_LOOP1  : -1,
        FUNC_MAIN              : -1,
        FUNC_MAIN__PTR_STR     : -1,
        FTBL_MAIN        : -1,
        FTBL_PRINT       : -1
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
    # Update the relative address OFFSET_STR
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

    string = "Hello, World!\n\0"
    bytecode.extend([ord(c) for c in string])

    ## === FUNCTION STRUCTURE SEGMENT == ##
    write_func_table_segment(
        bytecode, func_name_dict, func_table, address_table
    )

    # Update the labels
    update_label_addr(bytecode, address_table)
    
    return bytecode