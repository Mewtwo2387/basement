#ifndef _INSTRUCTION_H
#define _INSTRUCTION_H

typedef enum {
    /*  Abort program and set the CPU state to FAILED */
    OP_ABORT = 0,
    /* No operation */
    OP_NOP,
    /* Halt code execution */
    OP_DONE,

    /* ---------- Stack manipulation instructions ---------- */

    /* Push the immediate argument to the stack */
    OP_LOAD_CONST,
    /* Push the value addressed by the immediate argument to the stack */
    OP_LOAD_ADDR,
    /* Pop the top element of the stack and store it to memory addressed by the
       immediate argument. */
    OP_STORE_ADDR,
    /* Pop an address from the stack and push the value the address points to
       to the stack. */
    OP_LOAD,
    /* Pop an address and a literal value. And use them to write to memory. */
    OP_STORE,
    /* Pop the top element of the stack and set it as the VM result. */
    OP_POP_RES,
    /* Remove the top element of the stack. */
    OP_DISCARD,
    /* Duplicate the top element of the stack. */
    OP_DUP,
    /* Swap the two topmost elements on the stack. */
    OP_SWAP_TOP,
    /* Swap the top element of the stack with another element in the stack with
       the immediate argument as the offset from the top.
       NOTE: Since the stack grows downwards, the offset value is positive. */
    OP_SWAP,

    /* ---------- Arithmetic operations ---------- */

    /* Pop two values from the stack, add them together and push the sum to the
       stack. */
    OP_ADD,
    /* Add the immediate argument to the top element of the stack. */
    OP_ADD_CONST,
    /* Add the value addressed by the immediate argument to the top element of
       the stack. */
    OP_ADD_ADDR,
    /* Pop two values from the stack, subtract one from the other and push the
       difference to the stack. */
    OP_SUB,
    /* Subtract the top element of the stack with the immediate argument. */
    OP_SUB_CONST,
    /* Subtract the top element of the stack with the value addressed by the
       immediate argument. */
    OP_SUB_ADDR,
    /* Pop two values from the stack, multiply the two together and push the
       product to the stack. */
    OP_MUL,
    /* Pop two values from the stack, divide the first popped value with the
       second popped value and push the quotient to the stack. */
    OP_DIV,
    /* Unary positive. It does nothing to the operand, and is added as a
       counterpart for the `OP_UN_NEGATIVE` instruction for completion. */
    OP_UN_POSITIVE,
    /* Unary negative. Pops a value from the stack, "negates" it, and push the
       result to the stack.
       Since the operands are unsigned integers, the "negation" is done by
       applying the following formula:
            `~n + 1`
       where `~` is the bitwise NOT operation and `n` is the operand. */
    OP_UN_NEGATIVE,

    /* ---------- Bitwise logical operations ---------- */

    /* Pop two values from the stack, apply bitwise OR operation, and push the
       result to the stack. */
    OP_OR,
    /* Pop two values from the stack, apply bitwise AND operation, and push the
       result to the stack. */
    OP_AND,
    /* Pop two values from the stack, apply bitwise NOR operation, and push the
       result to the stack. */
    OP_NOR,
    /* Pop two values from the stack, apply bitwise NAND operation, and push the
       result to the stack. */
    OP_NAND,
    /* Pop two values from the stack, apply bitwise XOR operation, and push the
       result to the stack. */
    OP_XOR,
    /* Pop two values from the stack and do a left bitshift operation to the
       first value by an amount specified by the second value. The result is
       pushed to the stack. */
    OP_LSH,
    /* Pop two values from the stack and do a right bitshift operation to the
       first value by an amount specified by the second value. The result is
       pushed to the stack. */
    OP_RSH,
    /* Pop a value from the stack, and apply bitwise NOT operation, and push the
       result to the stack. */
    OP_NOT,

    /* ---------- Comparison operations ---------- */

    /* Pop two values from the stack, compare if the two values are equal, push
       1 if true else push 0 to the stack. */
    OP_EQ,
    /* Pop two values from the stack, compare if the first value is less than
       the second one, push 1 if true else push 0 to the stack. */
    OP_LT,
    /* Pop two values from the stack, compare if the first value is less than
       or equal to the second one, push 1 if true else push 0 to the stack. */
    OP_LEQ,
    /* Pop two values from the stack, compare if the first value is greater than
       the second one, push 1 if true else push 0 to the stack. */
    OP_GT,
    /* Pop two values from the stack, compare if the first value is greater than
       or equal to the second one, push 1 if true else push 0 to the stack. */
    OP_GEQ,


    /* ---------- Input/Output instructions ---------- */

    /* Get a value from the STDIN and push it to the stack. */
    OP_IN,
    /* Pop a value from the stack and print it to STDOUT as an ASCII
       character. */
    OP_OUT_CHAR,
    /* Pop a value from the stack and print it to STDOUT as a base-16
       integer. */
    OP_OUT_NUM,
    /* Print the instruction pointer as a base-16 integer. */
    OP_OUT_IP,
    /* Print the stack pointer as a base-16 integer. */
    OP_OUT_SP,
    /* Print the value addressed by the immediate argument as a base-16
       integer. */
    OP_OUT_ADDR,

    /* ---------- Jump instructions ---------- */

    /* Unconditional jump to the address supplied by the immediate argument. */
    OP_JUMP_ADDR,
    /* Jump to the address supplied by the immediate argument if the top element
       of the stack is 0. */
    OP_JMPZ_ADDR,
    /* Jump to the address supplied by the immediate argument if the top element
       of the stack is not 0. */
    OP_JMPNZ_ADDR,
    /* Pop an address from the stack and unconditionally jump to it.*/
    OP_JUMP,
    /* Pop an address and a value from the stack. If the value is 0, jump to
       the address. Otherwise, skip to the next instruction. */
    OP_JMPZ,
    /* Pop an address and a value from the stack. If the value is not 0, jump to
       the address. Otherwise, skip to the next instruction. */
    OP_JMPNZ,
    
    /* Function instructions */

    /* Jump the execution to the address of the function. Prior to this,
        several instructions are to be done:
            1. Push a reserved return value.
            2. Push the function arguments.
            3. Push the number of arguments.
            4. Push the return address which at this point should be the current
               instruction pointer.
        The sequence of data that is pushed to the stack shall be referred to as
        the "call frame".
        After the jump has been executed, the frame pointer moves to the top of
        the stack, which should have the return address. */
    OP_CALL,

    /* Return the execution from the function. This instruction execute the
        following instructions:

        1. Swap the top element of the stack with the reserved return value at
           the bottom of the topmost call frame. The return value is accessed
           through the frame pointer by calculating its address:

                    `FP + (N + 1)*W`

           where `N` is the number of arguments and `FP` is the frame pointer.
           (Note that the stack grows downwards so a "decrement" amounts to
            adding an offset to the address.)

           If the stack pointer is the same as the frame pointer, i.e. the
           execution of the function resulted to no value, no swapping is done.

        2. The stack pointer is decremented by `(N + 1)*W` such that it points
           to the return value.
        3. Then the instruction pointer is set as the return address, acccessed
           through the frame pointer.
        4. The frame pointer is then set to equal to the stack pointer.
           This action effectively pops off the call frame from the stack. */
    OP_RET
} Instruction_t;

#endif