#ifndef _INSTRUCTION_H
#define _INSTRUCTION_H

typedef enum {
    /*  Abort program and set the CPU state to FAILED */
    OP_ABORT = 0x00,
    /* No operation */
     OP_NOP = 0x01,
    /* Halt code execution */
    OP_DONE = 0x02,


    /* ---------- Stack manipulation instructions ---------- */

    /* Push the immediate argument of sizes 8, 16, 32 or 64 bits to the stack */
    OP_LOAD8_CONST =  0x10,
    OP_LOAD16_CONST = 0x11,
    OP_LOAD32_CONST = 0x12,
    OP_LOAD64_CONST = 0x13,

    /*
       Push value of size 8, 16, 32 or 64 bits addressed by the word sized
       immediate argument to the stack
    */
    OP_LOAD8_ADDR  = 0x20,
    OP_LOAD16_ADDR = 0x21,
    OP_LOAD32_ADDR = 0x22,
    OP_LOAD64_ADDR = 0x23,

    /*
      Pop the word sized top element of the stack and store it to memory
      addressed by the immediate argument as a value of size 8, 16, 32, or 64.
    */
    OP_STORE8_ADDR  = 0x30,
    OP_STORE16_ADDR = 0x31,
    OP_STORE32_ADDR = 0x32,
    OP_STORE64_ADDR = 0x33,

    /*
       Pop a word sized address from the stack and push the value of
       size 8, 16, 32 or 64 the address points to to the stack.
    */
    OP_LOAD8  = 0x40,
    OP_LOAD16 = 0x41,
    OP_LOAD32 = 0x42,
    OP_LOAD64 = 0x43,

    /*
       Pop a word sized address and a word sized value from the stack,
       mask the value to its supposed size (i.e. 8, 16, 32, 64 bits), and write
       the value to memory with the obtained address.
    */

    OP_STORE8  = 0x50,
    OP_STORE16 = 0x51,
    OP_STORE32 = 0x52,
    OP_STORE64 = 0x53,


    /*
        Push a value of size `N` to the stack from a call frame element a
        number of bytes away the frame pointer whose offset value is
        supplied by the `W` size immediate argument.
        This is used to access the arguments and local variables of a function.
    */

    OP_LOAD8_OFF_FP  = 0x60,
    OP_LOAD16_OFF_FP = 0x61,
    OP_LOAD32_OFF_FP = 0x62,
    OP_LOAD64_OFF_FP = 0x63,

    /*
        Store the `W` sized top element of the stack to a stack element
        a number of bytes away from the frame pointer, the offset value of
        which is to be provided by a `W` sized immediate argument.
    */
    OP_STORE8_OFF_FP  = 0x70,
    OP_STORE16_OFF_FP = 0x71,
    OP_STORE32_OFF_FP = 0x72,
    OP_STORE64_OFF_FP = 0x73,


    /* Push the instruction pointer to the stack as a word sized integer */
    OP_LOAD_IP = 0x80,
    /* Push the stack pointer to the stack as a word sized integer */
    OP_LOAD_SP = 0x81,
    /* Push the frame pointer to the stack as a word sized integer */
    OP_LOAD_FP = 0x82,

    /*
        Pop the word sized top element of the stack and set it as the VM result
    */
    OP_POP_RES = 0x83,
    /* Pop and discard the word sized top element of the stack. */
    OP_DISCARD = 0x84,
    /* Duplicate the word sized top element of the stack. */
    OP_DUP = 0x85,
    /* Swap the two topmost word sized elements on the stack. */
    OP_SWAP_TOP = 0x86,
    /*
        Swap the word sized top element of the stack with another word sized
        element in the stack with the immediate argument as the offset from the
        top.
    */
    OP_SWAP = 0x87,


    /* ---------- Arithmetic operations ---------- */
    /*
        Pop two word sized values from the stack, add them together and
        push the sum to the stack.
    */
    OP_ADD = 0x90,

    /* Add the immediate argument to the word sized top element of sthe stack */
    OP_ADD_CONST = 0x91,

    /*
        Pop two word sized values from the stack, subtract one from the other
        and push the difference to the stack.
    */
    OP_SUB = 0x92,

    /*
        Pop two word sized values from the stack, multiply the two together and
        push the product to the stack.
    */
    OP_MUL = 0x93,

    /*
        Pop two word sized values from the stack, divide the first popped value
        with the second popped value and push the quotient to the stack.
    */
    OP_DIV = 0x94,

    /*
        Unary positive. Consume a word sized operand from the stack and return
        it as is.
        Implementation-wise, this amounts to doing nothing like `OP_NOP`,
        except it throws an error if there is nothing on the stack since this is
        still a unary operator.
    */
    OP_UN_POSITIVE = 0x95,

    /*
        Unary negative. Pops a word sized value from the stack, "negates" it,
        and push the result to the stack.
        Since the operands are unsigned integers, the "negation" is done by
        applying the following formula:
             `~n + 1`
        where `~` is the bitwise NOT operation and `n` is the operand.
    */
    OP_UN_NEGATIVE = 0x96,


    /* ---------- Bitwise logical operations ---------- */
    /*
        Pop two word sized values from the stack, apply bitwise OR operation,
        and push the result to the stack.
    */
    OP_OR = 0x97,

    /*
        Pop two word sized values from the stack, apply bitwise AND operation,
        and push the result to the stack.
    */
    OP_AND = 0x98,

    /* 
        Pop two word sized values from the stack, apply bitwise NOR operation,
        and push the result to the stack.
    */
    OP_NOR = 0x99,

    /*
        Pop two word sized values from the stack, apply bitwise NAND operation,
        and push the result to the stack.
    */
    OP_NAND = 0x9A,

    /*
        Pop two word sized values from the stack, apply bitwise XOR operation,
        and push the result to the stack.
    */
    OP_XOR = 0x9B,

    /* 
        Pop two word sized values from the stack and do a left bitshift
        operation to the first value by an amount specified by the second value.
        The result is then pushed to the stack.
    */
    OP_LSH = 0x9C,

    /*
        Pop two word sized values from the stack and do a right bitshift
        operation to the first value by an amount specified by the second value.
        The result is then pushed to the stack.
    */
    OP_RSH = 0x9D,

    /* 
        Pop a value from the stack, and apply bitwise NOT operation,
        and push the result to the stack.
    */
    OP_NOT = 0x9E,

     /* ---------- Comparison operations ---------- */
    /*
        Pop two word sized values from the stack, compare if the two values are
        equal, push 1 if true else push 0 to the stack.
    */
    OP_EQ = 0xA0,

    /*
        Pop two word sized values from the stack, compare if the first value is
        less than the second one, push 1 if true else push 0 to the stack.
    */
    OP_LT = 0xA1,

    /*
        Pop two word sized values from the stack, compare if the first value is
        less than or equal to the second one, push 1 if true else push 0 to the
        stack.
    */
    OP_LEQ = 0xA2,

    /*
        Pop two word sized values from the stack, compare if the first value is
        greater than the second one, push 1 if true else push 0 to the stack.
    */
    OP_GT = 0xA3,

    /*
        Pop two word sized values from the stack, compare if the first value is
        greater than or equal to the second one, push 1 if true else push 0 to
        the stack.
    */
    OP_GEQ = 0xA4,


    /* ---------- Input/Output instructions ---------- */
    /*
        Get a value from the STDIN and push it to the stack as a
        word sized value.
    */
    OP_IN = 0xB0,

    /*
        Pop a word sized value from the stack and print it to STDOUT as an ASCII
        character.
    */
    OP_OUT_CHAR = 0xB1,

    /*
        Pop a word sized value from the stack and print it to STDOUT as an 
        integer in hexadecimal.
    */
    OP_OUT_NUM = 0xB2,

    /* Print the instruction pointer as a base-16 integer. */
    OP_OUT_IP = 0xB3,

    /* Print the stack pointer as a base-16 integer. */
    OP_OUT_SP = 0xB4,

    /* 
        Print the word sized value addressed by the immediate argument as an
        integer in hexadecimal.
    */
    OP_OUT_ADDR = 0xB5,


    /* ---------- Jump instructions ---------- */

    /* Unconditional jump to the address supplied by the immediate argument. */
    OP_JUMP_ADDR = 0xC0,

    /*
        Jump to the address supplied by the immediate argument if the word sized
        top element of the stack is 0.
    */
    OP_JMPZ_ADDR = 0xC1,

    /*
        Jump to the address supplied by the immediate argument if the word sized
        top element of the stack is not 0.
    */
    OP_JMPNZ_ADDR = 0xC2,

    /* Pop a word sized address from the stack and unconditionally jump to it.*/
    OP_JUMP = 0xC3,

    /*
        Pop a word sized address from the stack. If the word sized value on top
        of the stack is 0, jump to the address. Otherwise, skip to the next
        instruction.
    */
    OP_JMPZ = 0xC4,

    /*
        Pop a word sized address from the stack. If the word sized value on top
        of the stack is not 0, jump to the address. Otherwise, skip to the next
        instruction.
    */
    OP_JMPNZ = 0xC5,


    /* ------- Function instructions ------- */

    /*
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
    */
    OP_CALL = 0xD0,

    /*
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
    */
    OP_RETURN = 0xD1
} Instruction_t;
 
#endif