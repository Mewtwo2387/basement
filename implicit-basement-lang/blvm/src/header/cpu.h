#ifndef _CPU_H
#define _CPU_H

#include <stdint.h>
#include <stddef.h>

#define END_STATE_MSG_LEN 256

typedef enum {
    HALT_SUCCESS,
    HALT_FAILED,
    RUNNING,
    UNINITIALIZED,
} CPUState_t;

typedef struct {
    CPUState_t state;
    char *state_msg;

    /* Memory (RAM). The size is determined by the user or some default value */
    uint8_t *memory;
    size_t mem_capacity;

    /* Instruction pointer */
    uint8_t *ip;
    /* Frame pointer */
    uint8_t *fp;
} CPU_t;

#endif