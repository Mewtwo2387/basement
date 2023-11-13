#include <stdlib.h>
#include <stdio.h>
#include <string.h>

#include "bit_util.h"

void word_to_bytes(uint8_t *dest_bytes, word_t src_word) {
    union word_bytes wb = { .word=src_word };
    memcpy(dest_bytes, wb.bytes, WORD_SIZE * sizeof(*dest_bytes));
}

word_t bytes_to_word(uint8_t *src_bytes) {
    union word_bytes wb;
    memcpy(wb.bytes, src_bytes, sizeof(word_t) * sizeof(*src_bytes));
    return wb.word;
}