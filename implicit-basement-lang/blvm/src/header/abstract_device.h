#ifndef ABSTRACT_DEVICE_H
#define ABSTRACT_DEVICE_H

#include "datasize.h"

typedef data_t (*device_getter_fp)(void *, addr_t);
typedef void   (*device_setter_fp)(void *, addr_t, data_t);
typedef void   (*device_free_fp)(void *);

typedef struct {
    void *device;
    device_getter_fp getter_fp;
    device_setter_fp setter_fp;
    addr_t lower_mem_lim;
    addr_t upper_mem_lim;
} Device_t;

#endif