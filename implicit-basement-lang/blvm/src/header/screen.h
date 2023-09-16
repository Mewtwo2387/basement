#ifndef SCREEN_H
#define SCREEN_H

#include "datasize.h"

typedef struct {
    addr_t screen_size;
} Screen_t;

void screen_setter(void *screen, addr_t addr, data_t value);
void screen_free(void *screen);

#endif