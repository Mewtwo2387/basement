import opcodes as op
import data_size
from data_size import WORD_SIZE
from dataclasses import dataclass


FILLER_BYTE_ARR = [0 for _ in range(WORD_SIZE - 1)]


@dataclass
class Function:
    arg_num      : int
    var_sec_size : int
    address      : int

    @property
    def call_frame_size(self):
        """
        Size of the function call frame in bytes. The call frame consists of the
        following elements:
            1. Argument section
            2. Local variable section
            3. Return address
        The argument section is always a multiple of WORD_SIZE, while the local
        variable section can have any size in bytes. The return address is
        always of has the size WORD_SIZE.
        """
        return ((self.arg_num + 1) * WORD_SIZE) + self.var_sec_size + WORD_SIZE
    
    @property
    def func_data_list(self):
        return [self.arg_num, self.var_sec_size, self.address]


def int_to_bytes(n, size):
    return [(n >> (s * 8)) & 0xFF for s in range(size)]


def load_dummy_bytes(name: str):
    return [name, *FILLER_BYTE_ARR]


def write_test_code():
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

    FTBL__FUNC_MAIN        = "ftbl__main"
    FTBL__FUNC_PRINT       = "ftbl__print"
    FUNC_PRINT             = "print"
    FUNC_PRINT__LOOP1      = "loop1"
    FUNC_PRINT__OFFSET_STR = "arg_offset_str"
    FUNC_PRINT__END_LOOP1  = "end_loop"
    FUNC_MAIN              = "main"
    FUNC_MAIN__PTR_STR     = "str_ptr"

    address_table = {
        FUNC_PRINT             : -1,
        FUNC_PRINT__LOOP1      : -1,
        FUNC_PRINT__OFFSET_STR : -1,
        FUNC_PRINT__END_LOOP1  : -1,
        FUNC_MAIN              : -1,
        FUNC_MAIN__PTR_STR     : -1,
        FTBL__FUNC_MAIN        : -1,
        FTBL__FUNC_PRINT       : -1
    }

    func_table = {
        FUNC_PRINT : Function(1, 0, -1),
        FUNC_MAIN  : Function(0, 0, -1)
    }
    ### CODE SEGMENT ###

    ### Driver code ###
    bytecode.append(op.OP_CALL)
    bytecode.extend(load_dummy_bytes(FTBL__FUNC_MAIN))
    bytecode.append(op.OP_DONE)

    ### Function: print ###
    # Update the `FUNC_PRINT` and `LOOP1` addresses
    address_table[FUNC_PRINT] = len(bytecode)
    address_table[FUNC_PRINT__LOOP1] = len(bytecode)
    # Update the relative address OFFSET_STR
    address_table[FUNC_PRINT__OFFSET_STR] = \
        func_table[FUNC_PRINT].call_frame_size

    # While loop condition
    bytecode.append(op.OP_LOAD64_OFF_FP)
    bytecode.extend(load_dummy_bytes(FUNC_PRINT__OFFSET_STR))

    bytecode.append(op.OP_LOAD8)

    bytecode.append(op.OP_JMPZ_ADDR)
    bytecode.extend(load_dummy_bytes(FUNC_PRINT__END_LOOP1))

    bytecode.append(op.OP_DISCARD)

    # Print one character at a time
    bytecode.append(op.OP_LOAD64_OFF_FP)
    bytecode.extend(load_dummy_bytes(FUNC_PRINT__OFFSET_STR))

    bytecode.append(op.OP_LOAD8)

    bytecode.append(op.OP_OUT_CHAR)

    # Go to the next character in the string.
    bytecode.append(op.OP_LOAD64_OFF_FP)
    bytecode.extend(load_dummy_bytes(FUNC_PRINT__OFFSET_STR))

    bytecode.append(op.OP_ADD_CONST)
    bytecode.extend(int_to_bytes(data_size.INT8_SIZE, WORD_SIZE))

    bytecode.append(op.OP_STORE64_OFF_FP)
    bytecode.extend(load_dummy_bytes(FUNC_PRINT__OFFSET_STR))

    bytecode.append(op.OP_JUMP_ADDR)
    bytecode.extend(load_dummy_bytes(FUNC_PRINT__LOOP1))

    # Update the `END_LOOP1` address
    address_table[FUNC_PRINT__END_LOOP1] = len(bytecode)

    bytecode.append(op.OP_DISCARD)
    
    bytecode.append(op.OP_LOAD32_CONST)
    bytecode.extend(int_to_bytes(0, WORD_SIZE))

    bytecode.append(op.OP_RETURN)

    ### Function: main ###
    # Update the `FUNC_MAIN` address
    address_table[FUNC_MAIN] = len(bytecode)

    bytecode.append(op.OP_LOAD64_CONST)
    bytecode.extend(load_dummy_bytes(FUNC_MAIN__PTR_STR))

    bytecode.append(op.OP_CALL)
    bytecode.extend(load_dummy_bytes(FTBL__FUNC_PRINT))

    bytecode.append(op.OP_DISCARD)

    bytecode.append(op.OP_LOAD32_CONST)
    bytecode.extend(int_to_bytes(0, WORD_SIZE))

    bytecode.append(op.OP_RETURN)

    ### CONSTANT SEGMENT ###
    # Update the `STR_PTR` address
    address_table[FUNC_MAIN__PTR_STR] = len(bytecode)

    string = "Hello, World!\n"
    bytecode.extend([ord(c) for c in string] + [0])

    ### FUNCTION STRUCTURE SEGMENT ###
    # Update the `FTBL__FUNC_PRINT` address
    address_table[FTBL__FUNC_PRINT] = len(bytecode)
    func_table[FUNC_PRINT].address = address_table[FUNC_PRINT]

    func_print_obj = func_table[FUNC_PRINT]
    func_print_data_bytes = \
        [int_to_bytes(i, WORD_SIZE) for i in func_print_obj.func_data_list]
    for byte_arr in func_print_data_bytes:
        bytecode.extend(byte_arr)
    
    # Update the `FTBL__FUNC_MAIN` address
    address_table[FTBL__FUNC_MAIN] = len(bytecode)
    func_table[FUNC_MAIN].address = address_table[FUNC_MAIN]

    func_main_obj = func_table[FUNC_MAIN]
    func_main_data_bytes = \
        [int_to_bytes(i, WORD_SIZE) for i in func_main_obj.func_data_list]
    for byte_arr in func_main_data_bytes:
        bytecode.extend(byte_arr)

    # Update the labels
    for i, elem in enumerate(bytecode):
        if isinstance(elem, str):
            address = address_table[elem]
            bytecode[i : i + WORD_SIZE] = int_to_bytes(address, WORD_SIZE)
    
    return bytecode


def main():
    bytecode = write_test_code()

    # Print header
    print("A Hello World program:")
    print("..|", *[f"{i:02x}" for i in range(16)], sep=" ",
          end=("\n" + "---"*(17)))
    for i, b in enumerate(bytecode):
        if (i % 16 == 0):
            print(f"\n{i:02x}| ", end="")
        print(f"{b:02x} ", end="")
    print("\n")

    with open("test.o", "wb") as file:
        file.write(bytearray(bytecode))


if __name__ == "__main__":
    main()