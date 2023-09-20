#ifndef ABSTRACT_DEVICE_H
#define ABSTRACT_DEVICE_H

#include "datasize.h"

/*  Device data getter.
    ARGS: (void *) device object, (word2_t) memory address */
typedef word1_t (*device_getter_fp)(void *, word2_t);

/*  Device data setter.
    ARGS: (void *) device object, (word2_t) memory address, (word1_t) data */
typedef void    (*device_setter_fp)(void *, word2_t, word1_t);

/* Device `free` subroutine. It frees any malloc'd memory in the device. */
typedef void    (*device_free_fp)(void *);

typedef struct {
    void *device;
    device_getter_fp getter_fp;
    device_setter_fp setter_fp;
    word2_t lower_mem_lim;
    word2_t upper_mem_lim;
} Device_t;

#endif