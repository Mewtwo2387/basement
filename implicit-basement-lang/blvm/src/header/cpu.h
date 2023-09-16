#ifndef CPU_H
#define CPU_H

#include <stddef.h>
#include "datasize.h"
#include "memory_mapper.h"

typedef struct  {
    /* Instruction pointer */
    word1_t *ip;

    /* Data stack pointer */
    word8_t *data_sp;
    /* Return stack pointer */
    word8_t *ret_sp;

    /* Memory mapper which includes the RAM, the stacks and the I/O interface */
    MemoryMapper_t *MM;
} CPU_t;


/* Interpreter results */
typedef enum {
    RESULT_SUCCESS,
    RESULT_FAILED
} vm_result;

/* Operations and their opcodes */
typedef enum {
    OP_NOP
    // TODO: Add the rest of the opcodes
} opcode;

void cpu_load_program(CPU_t *cpu, word8_t *program, size_t program_size);
vm_result cpu_run(CPU_t *cpu);
void free_cpu(CPU_t *cpu);

#endif