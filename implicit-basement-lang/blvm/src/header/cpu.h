#ifndef _CPU_H
#define _CPU_H

#include <stdint.h>
#include <stddef.h>

#define MEM_SIZE_DEFAULT   65536
#define END_STATE_MSG_LEN  256

typedef enum {
    HALT_SUCCESS = 0,
    HALT_FAILED,
    RUNNING,
    UNINITIALIZED,
    STATE_UNKNOWN,

    /* Exclusive upper bound of CPU state enum */
    CPU_STATE_UBOUND,
} CPUState_t;

typedef struct {
    CPUState_t state;
    char *state_msg;

    /* Memory (RAM) */
    uint8_t *memory;
    size_t mem_size;

    /* The lower and upper bounds of the program */
    uint8_t *prog_bounds[2];

    /* Instruction pointer */
    uint8_t *ip;
    /* Stack pointer */
    uint8_t *sp;
    /* Frame pointer */
    uint8_t *fp;
} CPU_t;


/* Initialize the virtual machine (VM) */
void init_cpu(CPU_t *cpu, size_t memory_size);
/* Load the progam in bytecodes to memory */
void cpu_load_program(CPU_t *cpu, uint8_t *prog_bytecode, size_t prog_size);
/* Run loaded program in the memory of the VM */
CPUState_t cpu_run(CPU_t *cpu);
/* Clear the VM memory */
void cpu_clear_memory(CPU_t *cpu);
/* Free allocated memory in VM */
void free_cpu(CPU_t *cpu);

#endif