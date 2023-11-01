#ifndef _WORD_UTIL_H
#define _WORD_UTIL_H

#include <stdint.h>
#include <stddef.h>

#include "data_size.h"

union word_bytes {
    word_t word;
    uint8_t bytes[sizeof(word_t)];
};

void word_to_bytes(uint8_t *dest_bytes, word_t src_word);
word_t bytes_to_word(uint8_t *src_bytes);

#endif