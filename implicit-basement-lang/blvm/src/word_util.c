#include <stdlib.h>
#include <stdio.h>
#include <string.h>

#include "word_util.h"

static union word_bytes {
    word_t word;
    uint8_t bytes[sizeof(word_t)];
};

void word_to_bytes(uint8_t *dest_bytes, word_t src_word) {
    union word_bytes wb = { .word=src_word };
    memcpy(dest_bytes, wb.bytes, sizeof(word_t) * sizeof(*dest_bytes));
}

word_t bytes_to_word(uint8_t *src_bytes) {
    union word_bytes wb;
    memcpy(wb.bytes, src_bytes, sizeof(word_t) * sizeof(*src_bytes));
    return wb.word;
}