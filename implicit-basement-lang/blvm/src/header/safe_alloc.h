/*
    "Safe" memory allocation functions.
    NOTE: This does not prevent memory leaks. This only checks invalid
          memory allocations.
*/

#ifndef _SAFE_ALLOC_H
#define _SAFE_ALLOC_H

#include <stddef.h>

void *safe_malloc(size_t size);
void *safe_calloc(size_t num, size_t size);
void *safe_realloc(void *ptr, size_t new_size);

#endif