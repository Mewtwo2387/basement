#ifndef ABSTRACT_DEVICE_H
#define ABSTRACT_DEVICE_H

#include <stdint.h>
#include <stddef.h>

typedef uint8_t (*device_getter_fp)(void *, size_t);
typedef void    (*device_setter_fp)(void *, size_t, uint8_t);

typedef struct {
    void *device;
    device_getter_fp getter_fp;
    device_setter_fp setter_fp;
    size_t lower_mem_lim;
    size_t upper_mem_lim;
} Device_t;

#endif