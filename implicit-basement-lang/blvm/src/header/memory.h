#ifndef MEMORY_H
#define MEMORY_H

#include <stdint.h>
#include <stddef.h>

typedef struct {
    uint8_t *memory;
    size_t capacity;
} RAM_t;

uint8_t RAM_getter(void *ram, size_t index);
void    RAM_setter(void *ram, size_t index, uint8_t value);

#define RAM_UPPER_MEM_LIM 0x3000   // Placeholder value
#define RAM_LOWER_MEM_LIM 0x8000   // Placeholder value

#endif