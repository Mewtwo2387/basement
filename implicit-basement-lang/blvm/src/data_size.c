#include "data_size.h"

const size_t WORD_SIZE = 8;

const size_t data_sizes[5] = {
    sizeof(uint8_t),
    sizeof(uint16_t),
    sizeof(uint32_t),
    sizeof(uint64_t),
    WORD_SIZE
};

const word_t data_bitmasks[5] = {
    (uint8_t)(~0),
    (uint16_t)(~0),
    (uint32_t)(~0),
    (uint64_t)(~0),
    ~0
};