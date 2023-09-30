#include <stdio.h>
#include <string.h>

#include "instruction.h"
#include "cpu.h"
#include "word_util.h"

#define MAX_PROG_SIZE 1024


#define ADD_WORD_TO_PROG(prog, idx, word)    \
    word_to_bytes(bytes, word);              \
    memcpy(prog + idx, bytes, WORD_SIZE);    \
    idx += WORD_SIZE;

void write_test_prog__add_2_num(uint8_t *bytes, size_t *prog_size);
void write_test_prog__func_test(uint8_t *bytes, size_t *prog_size);
void print_bytes(uint8_t *bytes, size_t bytes_size);

int main(void) {
    CPU_t cpu;
    uint8_t program[MAX_PROG_SIZE] = { 0 };
    size_t prog_size;

    write_test_prog__func_test(program, &prog_size);
    print_bytes(program, prog_size);

    init_cpu(&cpu, MEM_SIZE_DEFAULT);
    cpu_load_program(&cpu, program, prog_size);
    
    cpu_run(&cpu);
    if (cpu.state == HALT_FAILED)
        fprintf(stderr, "VM failed: %s\n", cpu.state_msg);

    free_cpu(&cpu);
    return 0;
}

/* Write the following program to the byte array.
    ```
    LOAD_CONST 0x1
    LOAD_CONST 0x2
    ADD
    OUT_NUM
    LOAD_CONST 0x0A   ; New line character
    OUT_CHAR
    DONE
    ```
*/
void write_test_prog__add_2_num(uint8_t *program, size_t *prog_size) {
    word_t word;
    uint8_t bytes[WORD_SIZE];
    size_t idx = 0;

    /* Push the first addend to the stack */
    program[idx++] = OP_LOAD_CONST;
    word_to_bytes(bytes, 1);
    memcpy(program + idx, bytes, WORD_SIZE);
    idx += WORD_SIZE;

    /* Push the second addend to the stack */
    program[idx++] = OP_LOAD_CONST;
    word_to_bytes(bytes, 2);
    memcpy(program + idx, bytes, WORD_SIZE);
    idx += WORD_SIZE;

    /* Push the ADD command */
    program[idx++] = OP_ADD;

    /* Push the print number command */
    program[idx++] = OP_OUT_NUM;

    /* Push a new line */
    program[idx++] = OP_LOAD_CONST;
    word_to_bytes(bytes, '\n');
    memcpy(program + idx, bytes, WORD_SIZE);
    idx += WORD_SIZE;

    /* Push the print char command */
    program[idx++] = OP_OUT_CHAR;

    /* Stop the execution */
    program[idx++] = OP_DONE;

    *prog_size = idx;
}

/* Write the following program to the byte array.

   Pseudocode:
        print(string) {
            while (*string) { putc(*string++); }
            return 0;
        }

        print("Hello, World!\n");
    
   Code:

   -----------------------------------------------------------------------------
   ```asm
   ;; Push the call frame
   LOAD_CONST 0x0           ; Reserve the return value.
   LOAD_CONST STRING_ADDR   ; Load the address to the string to be printed.
   LOAD_CONST 0x1           ; Load the number of arguments
   CALL PRINT_FUNC          ; Call the print function
   DONE

   PRINT_FUNC:
        ;; Load the string address argument to the stack
        LOAD_FP         ; Get the frame pointer
        ADD_CONST 0x10  ; Skip the two elements on top of the stack to reach
                        ; the function argument: the string address.
                        ; NOTE:  1.) 0x10 = WORD_SIZE * 2. where WORD_SIZE = 8
                        ;        2.) Adding smth to the stack ptr decrements it
                        ;            Subtracting the stack ptr increments it
        LOAD            ; Load the value of the argument, the string address
        PRINT_LOOP:
            DUP                  ; Duplicate the top which should be string ptr
            LOAD                 ; Load the data addressed by the string ptr
            LOAD_CONST 0xFF      ; Push the byte bit mask
            AND                  ; Get only the first byte from the word
            JMPZ_ADDR EXIT_LOOP  ; Exit the print loop if 0x00 is encountered
            OUT_CHAR             ; Print the character to stdin.
            ADDI_CONST 0x1       ; Increment the string pointer by 1 byte.
            JUMP_ADDR PRINT_LOOP ; Repeat
        EXIT_LOOP:
        LOAD_CONST 0x0           ; Push the return value of the function
        RET
    ;; End of the print function

    ;; <-- string literals live here --> 
   ```
   -----------------------------------------------------------------------------
*/
void write_test_prog__func_test(uint8_t *program, size_t *prog_size) {
    word_t word;
    uint8_t bytes[WORD_SIZE];
    size_t idx = 0;

    const char str_input[] = "Hello, World!\n";

    /* Label index (pointer) and their corresponding values
       In this case, there are 4 labels. In the assembler, the labels and their
       names are counted on the first pass through the code.
     */

    #define LABEL_COUNT 4
    #define STRING_ADDR_LBL 0
    #define PRINT_FUNC_LBL  1
    #define PRINT_LOOP_LBL  2
    #define EXIT_LOOP_LBL   3

    size_t label_invoc_idx[LABEL_COUNT] = { 0 };   // Label invocation address
    word_t label_addr[LABEL_COUNT] = { 0 };        // Label address value
    const word_t dummy_word = 0xffffffffffffffff;

    /* ---------------------------------------------------------------------- */
    /* Writing the code proper.                                               */
    /* ---------------------------------------------------------------------- */

    /* Reserve the return value */
    program[idx++] = OP_LOAD_CONST;
    ADD_WORD_TO_PROG(program, idx, 0x0);

    /* Reserve the string address value. It will be added later */
    program[idx++] = OP_LOAD_CONST;
    label_invoc_idx[STRING_ADDR_LBL] = idx;
    ADD_WORD_TO_PROG(program, idx, dummy_word);

    /* Push the number of arguments to the stack */
    program[idx++] = OP_LOAD_CONST;
    ADD_WORD_TO_PROG(program, idx, 0x1);

    /* Call the print function. The function address will be added later */
    program[idx++] = OP_CALL;
    label_invoc_idx[PRINT_FUNC_LBL] = idx;
    ADD_WORD_TO_PROG(program, idx, dummy_word);

    /* Finish executing the program */
    program[idx++] = OP_DONE;

    /* Define the print function */
    label_addr[PRINT_FUNC_LBL] = idx;  // Register the print function address

    /* Load the string address argument to the stack */
    program[idx++] = OP_LOAD_FP;
    program[idx++] = OP_ADD_CONST;
    ADD_WORD_TO_PROG(program, idx, 0x2 * WORD_SIZE);
    program[idx++] = OP_LOAD;

    /* Start the print loop */
    label_addr[PRINT_LOOP_LBL] = idx;   // Register the print loop address

    /* Get the character to be printed. */
    program[idx++] = OP_DUP;
    program[idx++] = OP_LOAD;
    program[idx++] = OP_LOAD_CONST;
    ADD_WORD_TO_PROG(program, idx, 0xff);  // Push the bit mask for 1 byte.
    program[idx++] = OP_AND;

    /* Exit loop if a null byte is encountered. */
    program[idx++] = OP_JMPZ_ADDR;
    label_invoc_idx[EXIT_LOOP_LBL] = idx;
    ADD_WORD_TO_PROG(program, idx, dummy_word);

    /* Otherwise print the element on top of the stack as a char
       NOTE: This instruction pops off the element to be printed, putting the
             current pointer to the string on top.
    */
    program[idx++] = OP_OUT_CHAR;

    /* Go to the next character in the string. */
    program[idx++] = OP_ADD_CONST;
    ADD_WORD_TO_PROG(program, idx, 0x1);

    /* Repeat the print loop */
    program[idx++] = OP_JUMP_ADDR;
    label_invoc_idx[PRINT_LOOP_LBL] = idx;
    ADD_WORD_TO_PROG(program, idx, dummy_word);

    label_addr[EXIT_LOOP_LBL] = idx;   // Register the loop exit address

    /* Push the return value (0) to the stack */
    program[idx++] = OP_LOAD_CONST;
    ADD_WORD_TO_PROG(program, idx, 0x0);

    /* Return from the function */
    program[idx++] = OP_RET;

    /* ---------------------------------------------------------------------- */
    /* End of code. Below are constant definitions                            */
    /* ---------------------------------------------------------------------- */

    /* The input string constant. */
    label_addr[STRING_ADDR_LBL] = idx;
    memcpy(program + idx, str_input, strlen(str_input));
    idx += strlen(str_input);
    program[idx++] = '\0';   // Add a null byte to terminate the string.


    /* ---------------------------------------------------------------------- */
    /* Fill in the label addresses.                                           */
    /* ---------------------------------------------------------------------- */

    ADD_WORD_TO_PROG(program, label_invoc_idx[STRING_ADDR_LBL],
        label_addr[STRING_ADDR_LBL]);
    ADD_WORD_TO_PROG(program, label_invoc_idx[PRINT_FUNC_LBL],
        label_addr[PRINT_FUNC_LBL]);
    ADD_WORD_TO_PROG(program, label_invoc_idx[PRINT_LOOP_LBL],
        label_addr[PRINT_LOOP_LBL]);
    ADD_WORD_TO_PROG(program, label_invoc_idx[EXIT_LOOP_LBL],
        label_addr[EXIT_LOOP_LBL]);
    
    *prog_size = idx;

    #undef LABEL_COUNT
    #undef STRING_ADDR_LBL
    #undef PRINT_FUNC_LBL 
    #undef PRINT_LOOP_LBL 
    #undef EXIT_LOOP_LBL
}

void print_bytes(uint8_t *bytes, size_t bytes_size) {    
    /* Print header */
    for (size_t i = 0x00; i < 0x10; ++i)
        printf("%2.2lx ", i);
    printf("\n");

    for (size_t i = 0; i < bytes_size; ++i) {
        if (i % 16 == 0)
            printf("\n");
        printf("%2.2x ", bytes[i]);
    }
    printf("\n");
}