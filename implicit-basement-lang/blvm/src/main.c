#include <stdio.h>
#include <string.h>

#include "instruction.h"
#include "cpu.h"
#include "word_util.h"

#define PROG_SIZE 50


void print_bytes(uint8_t *bytes, size_t bytes_size);

int main(void) {
    CPU_t cpu;
    uint8_t prog_bytecode[PROG_SIZE] = { 0 };
    size_t idx = 0;

    // For translation
    word_t word;
    uint8_t bytes[WORD_SIZE];

    /* The Program in Basement assembly
        LOAD_CONST 0x1
        LOAD_CONST 0x2
        ADD
        OUT_NUM
        LOAD_CONST 0x0A   ; New line character
        OUT_CHAR
        DONE
    */

    /* Push the first addend to the stack */
    prog_bytecode[idx++] = OP_LOAD_CONST;
    word_to_bytes(bytes, 1);
    memcpy(prog_bytecode + idx, bytes, WORD_SIZE);
    idx += WORD_SIZE;

    /* Push the first addend to the stack */
    prog_bytecode[idx++] = OP_LOAD_CONST;
    word_to_bytes(bytes, 2);
    memcpy(prog_bytecode + idx, bytes, WORD_SIZE);
    idx += WORD_SIZE;

    /* Push the ADD command */
    prog_bytecode[idx++] = OP_ADD;

    /* Push the print number command */
    prog_bytecode[idx++] = OP_OUT_NUM;

    /* Push a new line */
    prog_bytecode[idx++] = OP_LOAD_CONST;
    word_to_bytes(bytes, '\n');
    memcpy(prog_bytecode + idx, bytes, WORD_SIZE);
    idx += WORD_SIZE;

    /* Push the print char command */
    prog_bytecode[idx++] = OP_OUT_CHAR;

    /* Stop the execution */
    prog_bytecode[idx++] = OP_DONE;

    print_bytes(prog_bytecode, idx);

    init_cpu(&cpu, MEM_SIZE_DEFAULT);
    cpu_load_program(&cpu, prog_bytecode, PROG_SIZE);
    
    cpu_run(&cpu);
    if (cpu.state == HALT_FAILED)
        fprintf(stderr, "VM failed: %s\n", cpu.state_msg);

    free_cpu(&cpu);
    return 0;
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