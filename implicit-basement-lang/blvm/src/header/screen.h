#ifndef SCREEN_H
#define SCREEN_H

#include "datasize.h"

typedef struct {
    word1_t *screen_buffer;
    word2_t  screen_size;
} Screen_t;

void screen_setter(void *screen, word2_t addr, word8_t value);
void screen_free(void *screen);

#endif