#ifndef STRING_TYPE_H
#define STRING_TYPE_H

#include <stddef.h>

typedef struct __string {
    char *data;
    size_t len;
    size_t capacity;
} string_t;

void init_string(string_t *str);
void string_append(string_t *str, char c);
char string_pop(string_t *str);
void free_string(string_t *str);

#endif