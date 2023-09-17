#ifndef DATASIZE_H
#define DATASIZE_H

#include <stdint.h>
#include <stddef.h>

typedef uint8_t  word1_t;
typedef uint16_t word2_t;
typedef uint64_t word8_t;


/*  N number of `word1_t` integers to a single `wordN_t` integer
    where N is in {2, 8}.
*/

word2_t word_to_word2(word1_t *array, size_t array_size);
word8_t word_to_word8(word1_t *array, size_t array_size);

#endif