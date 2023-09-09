#ifndef TYPE_H
#define TYPE_H

#include <stdint.h>
#include <stddef.h>
#include "string_type.h"

struct memory {
    uint8_t *data;
    size_t data_size;
    size_t data_ptr;

    string_t *instruction;
    size_t instr_ptr;
    size_t instr_count;

    size_t *stack;
    size_t stack_size;
    size_t stack_ptr;
};

#endif