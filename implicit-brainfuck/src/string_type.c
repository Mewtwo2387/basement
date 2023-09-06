#include <stdlib.h>
#include <stdio.h>
#include <string.h>

#include "string_type.h"
#include "safe_alloc.h"

#define GROWTH_FACTOR 3 / 2
#define INIT_CAPACITY 32

void init_string(string_t *str) {
    str->capacity = INIT_CAPACITY;
    str->len = 0;
    str->data = safe_calloc( INIT_CAPACITY, sizeof(*(str->data)) );
}

static void resize_str(string_t *str) {
    str->capacity = str->capacity * GROWTH_FACTOR;
    str->data = safe_realloc(str->data, str->capacity);
    // Fill the newly allocated memory with null char
    memset(str->data + str->len, 0, str->capacity - str->len);
}

void string_append(string_t *str, char c) {
    if (str->len == str->capacity) {
        resize_str(str);
    }
    str->data[str->len++] = c;
}

char string_pop(string_t *str) {
    if (str->len == 0) {
        fprintf(stderr, "you cant just pop a char off an empty string, smh\n");
        exit(1);
    }
    char c = str->data[--str->len];
    str->data[str->len] = '\0';
    return c;
}

void free_string(string_t *str) {
    free(str->data);
    str->capacity = 0;
    str->len = 0;
}