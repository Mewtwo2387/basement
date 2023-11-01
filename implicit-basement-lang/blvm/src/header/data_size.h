#ifndef _DATA_SIZE_H
#define _DATA_SIZE_H

#include <stdint.h>
#include <stddef.h>

typedef uint64_t word_t;

/* NOTE: Indices match with the lower four bits of the LOAD/STORE opcodes. */
enum DATA_SIZE_IDX {
    DSZ_IDX_INT8  = 0,
    DSZ_IDX_INT16 = 1,
    DSZ_IDX_INT32 = 2,
    DSZ_IDX_INT64 = 3,
    DSZ_IDX_WORD
};

extern const size_t WORD_SIZE;
extern const size_t data_sizes[5];
extern const word_t data_bitmasks[5];

#endif