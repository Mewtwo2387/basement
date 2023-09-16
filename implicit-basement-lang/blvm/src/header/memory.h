#ifndef MEMORY_H
#define MEMORY_H

#include "datasize.h"

typedef struct {
    data_t *memory;
    addr_t capacity;
} RAM_t;

data_t RAM_getter(void *ram, addr_t addr);
void   RAM_setter(void *ram, addr_t addr, data_t value);
void   RAM_free(void *ram);

#define RAM_UPPER_ADDR_LIM 0x3000   // Placeholder value
#define RAM_LOWER_ADDR_LIM 0x8000   // Placeholder value

#endif