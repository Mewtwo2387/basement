#ifndef CPU_H
#define CPU_H

#include <stdint.h>
#include "memory_mapper.h"

typedef struct  {
    uint8_t ip;
    MemoryMapper_t *MM;
} CPU_t;


#endif