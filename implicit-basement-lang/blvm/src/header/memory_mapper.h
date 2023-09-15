#ifndef MEMORY_MAPPER_H
#define MEMORY_MAPPER_H

#include <stdint.h>
#include <stddef.h>
#include "abstract_device.h"

typedef struct {
    Device_t *device_arr;
    size_t device_count;
} MemoryMapper_t;

void    init_memory_mapper(MemoryMapper_t *MM);
void    memory_mapper_map_device(MemoryMapper_t *MM, void *device,
                                 device_getter_fp getter,
                                 device_setter_fp setter,
                                 size_t lower_mem_lim,
                                 size_t upper_mem_lim);
uint8_t memory_mapper_get(MemoryMapper_t *MM, size_t index);
void    memory_mapper_set(MemoryMapper_t *MM, size_t index, uint8_t value);

#endif