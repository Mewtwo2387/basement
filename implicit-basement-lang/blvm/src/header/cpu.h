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
    CPU_STATE_MAX,
} CPUState_t;

typedef struct {
    CPUState_t state;
    char *state_msg;

    /* Memory (RAM). The size is determined by the user or some default value */
    uint8_t *memory;
    size_t mem_size;
    uint8_t *prog_bounds[2]; // The lower and upper bounds of the program.
    uint8_t *heap_ptr;       // Pointer to the top of the heap.

    /* Instruction pointer */
    uint8_t *ip;
    /* Stack pointer */
    uint8_t *sp;
    /* Frame pointer */
    uint8_t *fp;
} CPU_t;


void init_cpu(CPU_t *cpu, size_t memory_size);
void cpu_load_program(CPU_t *cpu, uint8_t *prog_bytecode, size_t prog_size);
CPUState_t cpu_run(CPU_t *cpu);
void cpu_clear_memory(CPU_t *cpu);
void free_cpu(CPU_t *cpu);

#endif