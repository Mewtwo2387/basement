#ifndef ERROR_H
#define ERROR_H

#include <stdint.h>
#include <stdbool.h>
#include "memory_type.h"

enum ERROR_TYPE {
    FILE_READ_FAILED,
    INSTR_OVERFLOW,
    INSTR_UNDERFLOW,
    DATA_OVERFLOW,
    DATA_UNDERFLOW,
    STACK_OVERFLOW,
    STACK_UNDERFLOW,
    SYNTAX_ERROR,
    UNKNOWN,
    CUSTOM
};

extern bool colored_error_msg;

void throw_error(enum ERROR_TYPE error_type, struct memory mem_snapshot,
                 char *add_msg, bool to_print_memory);

#endif
