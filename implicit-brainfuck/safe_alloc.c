#include <stdlib.h>
#include <stdio.h>
#include "safe_alloc.h"

#define ALLOC_GUARD(ptr, name)               \
    if (ptr == NULL) {                       \
        fprintf(stderr, "%s failed.", name); \
        exit(1);                             \
    }

void *safe_malloc(size_t size) {
    void *ptr = malloc(size);
    ALLOC_GUARD(ptr, "malloc")
    return ptr;
}

void *safe_calloc(size_t num, size_t size) {
    void *ptr = calloc(num, size);
    ALLOC_GUARD(ptr, "calloc")
    return ptr;
}

void *safe_realloc(void *ptr, size_t new_size) {
    void *ptr = realloc(ptr, new_size);
    ALLOC_GUARD(ptr, "realloc")
    return ptr;
}