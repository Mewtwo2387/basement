#include <stdlib.h>
#include <stdio.h>
#include <string.h>

#include "byte_array.h"
#include "safe_alloc.h"
#include "error.h"

#define GROWTH_FACTOR 3 / 2
#define ERR_MSG_LEN 150

void init_byte_arr(byte_arr_t *array, size_t init_length, bool is_dynamic) {
    *array = (byte_arr_t){
        .len = init_length,
        .is_dynamic = is_dynamic
    };
    array->data = calloc(init_length, sizeof(*array->data));
}

static void resize_array(byte_arr_t *array, size_t included_index) {
    // NOTE: Length below 2 would not grow, so we set them to 2.
    if (included_index < 2)
        included_index = 2;

    size_t new_len = included_index * GROWTH_FACTOR;
    array->data = safe_realloc(array->data, new_len);
    /* Fill the newly allocated memory with zeros. */
    memset(array->data + array->len, 0, new_len - array->len);
    array->len = new_len;
}

void byte_arr_set(byte_arr_t *array, size_t index, uint8_t c) {
    if (index >= array->len) {
        if (array->is_dynamic) {
            resize_array(array, index);
        } else {
            char *error_msg = calloc(ERR_MSG_LEN + 1, sizeof(*error_msg));
            sprintf(error_msg,
                    "Attempted to set a value to a static byte array"
                    " at index %ld beyond its length (%ld)",
                    index, array->len);
            throw_error(CUSTOM, (struct memory){ 0 }, error_msg, false);
        }
    }
    array->data[index] = c;
}

uint8_t byte_arr_get(byte_arr_t *array, size_t index) {
    if (index >= array->len) {
        if (array->is_dynamic) {
            resize_array(array, index);
        } else {
            char *error_msg = calloc(ERR_MSG_LEN + 1, sizeof(*error_msg));
            sprintf(error_msg,
                    "Index %ld is out of bounds (length: %ld)",
                    index, array->len);
            throw_error(CUSTOM, (struct memory){ 0 }, error_msg, false);
        }
    }
    return array->data[index];
}

void byte_arr_resize(byte_arr_t *array, size_t new_len) {
    if (!array->is_dynamic) {
        throw_error(CUSTOM, (struct memory){ 0 },
                    "Attempted to resize a static byte array", false);
    }

    array->data = safe_realloc(array->data, new_len);

    /* If the new length includes new memory, fill them with 0's. */
    if (new_len > array->len)
        memset(array->data + array->len, 0, new_len - array->len);
    
    array->len = new_len;
}

void free_byte_arr(byte_arr_t *array) {
    free(array->data);
    array->len = 0;
}