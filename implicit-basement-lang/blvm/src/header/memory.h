#ifndef MEMORY_H
#define MEMORY_H

#include "datasize.h"

typedef struct {
    word1_t *memory;
    word2_t  capacity;
} RAM_t;

word1_t RAM_getter(void *ram, word2_t addr);
void    RAM_setter(void *ram, word2_t addr, word1_t value);
void    RAM_free(void *ram);

#define RAM_UPPER_ADDR_LIM 0x3000   // Placeholder value
#define RAM_LOWER_ADDR_LIM 0x8000   // Placeholder value

#endif