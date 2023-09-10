#ifndef BYTE_ARRAY_H
#define BYTE_ARRAY_H

#include <stddef.h>
#include <stdint.h>
#include <stdbool.h>

typedef struct __byte_array {
    uint8_t *data;
    size_t len;
    bool is_dynamic;
} byte_arr_t;

void    init_byte_arr(byte_arr_t *array, size_t init_length, bool is_dynamic);
void    byte_arr_set(byte_arr_t *array, size_t index, uint8_t c);
uint8_t byte_arr_get(byte_arr_t *array, size_t index);
void    byte_arr_resize(byte_arr_t *array, size_t new_len);
void    free_byte_arr(byte_arr_t *array);

#endif