#ifndef INPUT_DEVICE_H
#define INPUT_DEVICE_H

#include "datasize.h"

typedef struct {
    addr_t keyboard_size;
} Keyboard_t;

data_t keyboard_getter(void *keyboard, addr_t addr);
void   keyboard_free(void *keyboard);

#endif