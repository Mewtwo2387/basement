## ---------- CPU State/Miscellaneous instructions ---------- ##
ABORT = 0x00
"""Abort program and set the CPU state to FAILED"""
NOP   = 0x01
""" No operation """
DONE  = 0x02
""" Halt code execution """


## ---------- Stack manipulation instructions ---------- ##
## Push the immediate argument to the stack
LOAD8_CONST  = 0x10
LOAD16_CONST = 0x11
LOAD32_CONST = 0x12
LOAD64_CONST = 0x13

## Push value of size 8, 16, 32 or 64 bits addressed by the word size
## immediate argument to the stack
LOAD8_ADDR  = 0x20
LOAD16_ADDR = 0x21
LOAD32_ADDR = 0x22
LOAD64_ADDR = 0x23

## Pop the word sized top element of the stack and store it to memory
## addressed by the immediate argument as a value of size 8, 16, 32, or 64.
STORE8_ADDR  = 0x30
STORE16_ADDR = 0x31
STORE32_ADDR = 0x32
STORE64_ADDR = 0x33


## Pop a word sized address from the stack and push the value of
## size 8, 16, 32 or 64 the address points to to the stack.
LOAD8  = 0x40
LOAD16 = 0x41
LOAD32 = 0x42
LOAD64 = 0x43


## Pop a word sized address and a word sized value from the stack,
## mask the value to its supposed size (i.e. 8, 16, 32, 64 bits), and write
## the value to memory with the obtained address.
STORE8  = 0x50
STORE16 = 0x51
STORE32 = 0x52
STORE64 = 0x53


## Push a value of size `N` to the stack from a call frame element a
## number of bytes away the frame pointer whose offset value is
## supplied by the `W` size immediate argument.
## This is used to access the arguments and local variables of a function.
LOAD8_OFF_FP  = 0x60
LOAD16_OFF_FP = 0x61
LOAD32_OFF_FP = 0x62
LOAD64_OFF_FP = 0x63


## Store the `W` sized top element of the stack to a stack element
## a number of bytes away from the frame pointer, the offset value of
## which is to be provided by a `W` sized immediate argument.
STORE8_OFF_FP  = 0x70
STORE16_OFF_FP = 0x71
STORE32_OFF_FP = 0x72
STORE64_OFF_FP = 0x73


LOAD_IP = 0x80
""" Push the instruction pointer to the stack as a word sized integer. """

LOAD_SP = 0x81
""" Push the stack pointer to the stack as a word sized integer. """

LOAD_FP = 0x82
""" Push the frame pointer to the stack as a word sized integer. """

PRES = 0x83
""" Pop the word sized top element of the stack and set it as the VM result. """

DISCARD = 0x84
""" Pop and discard the word sized top element of the stack. """

DUP = 0x85
""" Duplicate the word sized top element of the stack. """

SWAP_TOP = 0x86
""" Swap the two topmost word sized elements on the stack. """

SWAP = 0x87
"""
    Swap the word sized top element of the stack with another word sized
    element in the stack with the immediate argument as the offset from the
    top.
"""


## ---------- Arithmetic operations ---------- ##
"""
    Pop two word sized values from the stack, add them together and
    push the sum to the stack.
"""
ADD = 0x90

ADD_CONST = 0x91
""" Add the immediate argument to the word sized top element of sthe stack. """

SUB = 0x92
"""
    Pop two word sized values from the stack, subtract one from the other
    and push the difference to the stack.
"""

MUL = 0x93
"""
    Pop two word sized values from the stack, multiply the two together and
    push the product to the stack.
"""

DIV = 0x94
"""
    Pop two word sized values from the stack, divide the first popped value
    with the second popped value and push the quotient to the stack.
"""

UN_POSITIVE = 0x95
"""
    Unary positive. Consume a word sized operand from the stack and return
    it as is.
    Implementation-wise, this amounts to doing nothing like `NOP`,
    except it throws an error if there is nothing on the stack since this is
    still a unary operator.
"""

UN_NEGATIVE = 0x96
"""
    Unary negative. Pops a word sized value from the stack, "negates" it,
    and push the result to the stack.
    Since the operands are unsigned integers, the "negation" is done by
    applying the following formula:
            `~n + 1`
    where `~` is the bitwise NOT operation and `n` is the operand.
"""


## ---------- Bitwise logical operations ---------- ##
OR = 0x97
"""
    Pop two word sized values from the stack, apply bitwise OR operation,
    and push the result to the stack.
"""

AND = 0x98
"""
    Pop two word sized values from the stack, apply bitwise AND operation,
    and push the result to the stack.
"""

NOR = 0x99
"""
    Pop two word sized values from the stack, apply bitwise NOR operation,
    and push the result to the stack.
"""

NAND = 0x9A
"""
    Pop two word sized values from the stack, apply bitwise NAND operation,
    and push the result to the stack.
"""

XOR = 0x9B
"""
    Pop two word sized values from the stack, apply bitwise XOR operation,
    and push the result to the stack.
"""

LSH = 0x9C
"""
    Pop two word sized values from the stack and do a left bitshift
    operation to the first value by an amount specified by the second value.
    The result is then pushed to the stack.
"""

RSH = 0x9D
"""
    Pop two word sized values from the stack and do a right bitshift
    operation to the first value by an amount specified by the second value.
    The result is then pushed to the stack.
"""

NOT = 0x9E
"""
    Pop a value from the stack, and apply bitwise NOT operation,
    and push the result to the stack.
"""

## ---------- Comparison operations ---------- ##
EQ = 0xA0
"""
    Pop two word sized values from the stack, compare if the two values are
    equal, push 1 if true else push 0 to the stack.
"""

LT = 0xA1
"""
    Pop two word sized values from the stack, compare if the first value is
    less than the second one, push 1 if true else push 0 to the stack.
"""

LEQ = 0xA2
"""
    Pop two word sized values from the stack, compare if the first value is
    less than or equal to the second one, push 1 if true else push 0 to the
    stack.
"""

GT = 0xA3
"""
    Pop two word sized values from the stack, compare if the first value is
    greater than the second one, push 1 if true else push 0 to the stack.
"""

GEQ = 0xA4
"""
    Pop two word sized values from the stack, compare if the first value is
    greater than or equal to the second one, push 1 if true else push 0 to
    the stack.
"""


## ---------- Input/Output instructions ---------- ##
IN = 0xB0
"""
    Get a value from the STDIN and push it to the stack as a word sized value.
"""

OUT_CHAR = 0xB1
"""
    Pop a word sized value from the stack and print it to STDOUT as an ASCII
    character.
"""

OUT_NUM = 0xB2
"""
    Pop a word sized value from the stack and print it to STDOUT as an 
    integer in hexadecimal.
"""

OUT_IP = 0xB3
""" Print the instruction pointer as a base-16 integer. """

OUT_SP = 0xB4
""" Print the stack pointer as a base-16 integer. """

OUT_ADDR = 0xB5
"""
    Print the word sized value addressed by the immediate argument as an
    integer in hexadecimal.
"""


## ---------- Jump instructions ---------- ##
JUMP_ADDR = 0xC0
"""
    Unconditional jump to the address supplied by the immediate argument.
"""

JMPZ_ADDR = 0xC1
"""
    Jump to the address supplied by the immediate argument if the word sized
    top element of the stack is 0.
"""

JMPNZ_ADDR = 0xC2
"""
    Jump to the address supplied by the immediate argument if the word sized
    top element of the stack is not 0.
"""

JUMP = 0xC3
"""
Pop a word sized address from the stack and unconditionally jump to it.   
"""

JMPZ = 0xC4
"""
    Pop a word sized address from the stack. If the word sized value on top
    of the stack is 0, jump to the address. Otherwise, skip to the next
    instruction.
"""

JMPNZ = 0xC5
"""
    Pop a word sized address from the stack. If the word sized value on top
    of the stack is not 0, jump to the address. Otherwise, skip to the next
    instruction.
"""

## ------- Function instructions ------- ##
CALL = 0xD0
"""
    Call a function, consume a number of word sized sized stack elements as
    the function arguments and push the result as a word sized integer to
    the stack.
    
    Implementation-wise, this instruction is comprised of multiple
    instructions.

    Firstly, the address provided by the immediate argument must lead to
    the function table element corresponding to the called function.

    Assuming the prerequisite mentioned above is met, then the following
    instructions are to be executed upon executing the CALL instruction:

    1. Obtain the number of function argument and push it to the stack as
        size in bytes, i.e. `n * W` where `n` is the number of arguments
        and `W` is the size of a word in bits.
    2. Obtain the size of the local variables and allocate a space for them.
        This is done by just incrementing the stack pointer with the said
        size.
        Then the size of the local variable section is pushed to the stack.
    3. The return address which, at this point, is the instruction pointer
        is pushed to the stack.
    4. The frame pointer is updated to point to the return address.
    5. Obtain the address to the function and have the instruction pointer
        point to that address.

    Upon finishing executing this instruction, on the stack is a call frame.
"""

RETURN = 0xD1
"""
    Return from the currently executing function and push the return value
    of the function to the stack.
    
    Like the CALL instruction, this instruction is comprised of multiple
    instructions.

    Firstly, the return value is pointed to by the stack pointer. This
    necessitates that there must be at least one word sized value above the
    call frame.

    Assuming that the prerequisite stated above is already met, the
    following instructions are executed:

    1. Set the instruction pointer with the return address accessed through
        frame pointer (FP). Decrement FP by a word size so that it is
        pointing to the next element in the call frame.
    2. Obtain the size of local variable and use it to decrement FP to reach
        the next element in the call frame.
    3. Obtain size of the argument section and use it to decrement FP to
        reach the bottom of the call frame.
    4. Copy the word sized value the stack pointer is pointing to to the
        memory FP is pointing to, overwriting a section of the call frame.
    5. Set the stack pointer as FP, effectively popping off the call frame
        from the stack.
"""