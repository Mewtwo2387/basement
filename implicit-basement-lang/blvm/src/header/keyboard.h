#ifndef INPUT_DEVICE_H
#define INPUT_DEVICE_H

#include "datasize.h"

typedef struct {
    word1_t *keyboard_buffer;
    word2_t  keyboard_size;
} Keyboard_t;

word8_t keyboard_getter(void *keyboard, word2_t addr);
void    keyboard_free(void *keyboard);

#endif