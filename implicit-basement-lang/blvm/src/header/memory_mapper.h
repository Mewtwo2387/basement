#ifndef MEMORY_MAPPER_H
#define MEMORY_MAPPER_H

#include <stddef.h>
#include "abstract_device.h"

typedef struct {
    Device_t *device_arr;
    size_t    device_count;
} MemoryMapper_t;

void    init_memory_mapper(MemoryMapper_t *MM, size_t device_count);
void    memory_mapper_map_device(MemoryMapper_t *MM, void *device,
                                 device_getter_fp getter,
                                 device_setter_fp setter,
                                 device_free_fp free_fun,
                                 word2_t lower_addr_lim,
                                 word2_t upper_addr_lim);
word1_t memory_map_get(MemoryMapper_t *MM, word2_t addr);
void    memory_map_set(MemoryMapper_t *MM, word2_t addr, word1_t value);
void    memory_map_free_devices(MemoryMapper_t *MM);

#endif