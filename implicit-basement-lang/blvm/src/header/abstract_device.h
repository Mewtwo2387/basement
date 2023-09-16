#ifndef ABSTRACT_DEVICE_H
#define ABSTRACT_DEVICE_H

#include "datasize.h"

typedef word8_t (*device_getter_fp)(void *, word2_t);
typedef void    (*device_setter_fp)(void *, word2_t, word8_t);
typedef void    (*device_free_fp)(void *);

typedef struct {
    void *device;
    device_getter_fp getter_fp;
    device_setter_fp setter_fp;
    word2_t lower_mem_lim;
    word2_t upper_mem_lim;
} Device_t;

#endif