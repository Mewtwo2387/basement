/******************************************************************************
            Yet ANother brainFuck intErpreter! (YANFE!)
                by: ImplicitNull/implicit none

    A Brainfuck implementation. Pronounced as /yan.fei/.

    Enabling indefinite data memory size turns this interpreter into the
    so called:

        Yet ANother brainFuck intErpreter! - Super Memory Usage proGram
    or
        YANFE!SMUG

*******************************************************************************/

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <stdbool.h>

#include "byte_array.h"
#include "memory_type.h"
#include "parse_arg.h"
#include "yanfeismug.h"
#include "error.h"


#define MAX_STACK_SIZE 1024

/* Memory */
byte_arr_t data;
byte_arr_t instruction;
size_t   stack[MAX_STACK_SIZE] = { (size_t)0 };

/* Dump file names */
const char *data_dump_name   = "datadump";
const char *stack_dump_name  = "stackdump";

const char *valid_bf_char = "+-<>.,[]";


void dump_memory_to_file(void) {
    FILE *data_dump_fp, *stack_dump_fp;
    data_dump_fp = fopen(data_dump_name, "wb");
    stack_dump_fp = fopen(stack_dump_name, "wb");

    fwrite(data.data, sizeof( *(data.data) ), data.len, data_dump_fp);
    fwrite(stack, sizeof(*stack), MAX_STACK_SIZE, stack_dump_fp);

    fclose(data_dump_fp);
    fclose(stack_dump_fp);
}

struct memory get_memory_snapshot(size_t data_ptr, size_t instr_ptr,
        size_t instr_count, size_t stack_ptr)
{
    struct memory memory_snapshot = {
        .data=data.data,
        .data_size=data.len,
        .data_ptr=data_ptr,

        .instruction=instruction.data,
        .instr_size=instruction.len,
        .instr_ptr=instr_ptr,
        .instr_count=instr_count,

        .stack=stack,
        .stack_size=MAX_STACK_SIZE,
        .stack_ptr=stack_ptr
    };

    return memory_snapshot;
}

int main(size_t argc, char* const argv[]) {
    struct cli_options options = parse_cli_args(argc, argv);

    /* Print a yanfeismug ASCII art to signal that this is now YANFE!SMUG*/
    if (options.mem_size == 0)
        print_yanfeismug();

    /* Set the colored output status */
    colored_error_msg = options.colored_txt;

    /* Read the input file */
    FILE *input_file_ptr = fopen(options.input_path, "r");
    if (input_file_ptr == NULL) {
        char *add_err_msg = calloc(strlen(options.input_path) + 15,
                                   sizeof(*add_err_msg));
        sprintf(add_err_msg, "Cannot read '%s'", options.input_path);
        throw_error(FILE_READ_FAILED, (struct memory){ 0 }, add_err_msg, false);
    }

    /* Load and filter out non-valid characters */
    char c;
    size_t instr_idx = 0;

    init_byte_arr(&instruction, 1, true);
    while ( fread(&c, 1, 1, input_file_ptr) ) {
        if ( strchr(valid_bf_char, c) != NULL )
            byte_arr_set(&instruction, instr_idx++, c);
    }
    fclose(input_file_ptr);

    /* Cut off the excess allocated memory in instruction */
    byte_arr_resize(&instruction, instr_idx);
    instruction.is_dynamic = false;    // Freeze the instruction size.

    /* Initialize the data memory */
    if (options.mem_size == 0)
        init_byte_arr(&data, OPT_MEM_SIZE * sizeof(*(data.data)), true);
    else
        init_byte_arr(&data, options.mem_size * sizeof(*(data.data)), false);

    /* Initialize pointers and counters */
    size_t data_ptr  = 0;
    size_t instr_ptr = 0;
    size_t stack_ptr = 0;
    size_t instr_count = 0;   // Count of all executed instructions

    /* 
        Evaluate the program 
        NOTE: The `get` and `set` routines of the byte array `instruction` are 
              not used here due to performance overhead. Risky but necessary.
    */
    while ( instr_ptr < instruction.len ) {
        switch ( (c = instruction.data[instr_ptr]) ) {
        case '+':
        case '-':
            char old_val = byte_arr_get(&data, data_ptr);
            char new_val = (c == '+')? old_val + 1 : old_val - 1;
            byte_arr_set(&data, data_ptr, new_val);
            break;
        case '>':
            ++data_ptr;
            break;
        case '<':
            --data_ptr;
            break;
        case '.':
            putc(byte_arr_get(&data, data_ptr), stdout);
            break;
        case ',':
            byte_arr_set(&data, data_ptr, getc(stdin));
            break;
        case '[':
            if ( byte_arr_get(&data, data_ptr) == 0 ) {
                // Skip the entire loop if 0
                int bracket_lvl = 0;
                
                while ( !(bracket_lvl == 1 && c == ']') ) {
                    if (c == '[') ++bracket_lvl;
                    if (c == ']') --bracket_lvl;

                    c = instruction.data[++instr_ptr];
                }

                if (instr_ptr == instruction.len && bracket_lvl > 0)
                    throw_error(SYNTAX_ERROR,
                                get_memory_snapshot(
                                    data_ptr, instr_ptr, instr_count, stack_ptr
                                ),
                               "Unbalanced brackets.", false);

            } else {
                if (stack_ptr == MAX_STACK_SIZE)
                    throw_error(STACK_OVERFLOW,
                                get_memory_snapshot(
                                    data_ptr, instr_ptr, instr_count, stack_ptr
                                ),
                                NULL, true);

                stack[stack_ptr++] = instr_ptr;
            }
            break;

        case ']':
            if (stack_ptr == 0)
                throw_error(STACK_UNDERFLOW,
                            get_memory_snapshot(
                                data_ptr, instr_ptr, instr_count, stack_ptr
                            ),
                            NULL, true);

            if ( byte_arr_get(&data, data_ptr) == 0 )
                --stack_ptr;
            else
                instr_ptr = stack[stack_ptr - 1];

            break;
        default:
            char *error_msg = calloc(40, sizeof(*error_msg));
            if (c == '\0')
                sprintf(error_msg, "Offending instruction: NULL byte");
            else
                sprintf(error_msg, "Offending instruction: '%c'", c);
            throw_error(UNKNOWN_INSTR, (struct memory){ 0 }, error_msg, false);
        }

        // Check for invalid data pointer values
        if (data_ptr == SIZE_MAX)
            throw_error(DATA_UNDERFLOW,
                        get_memory_snapshot(
                            data_ptr, instr_ptr, instr_count, stack_ptr
                        ),
                        NULL, true);
        if ( (data_ptr >= data.len) && !data.is_dynamic )
            throw_error(DATA_OVERFLOW,
                        get_memory_snapshot(
                            data_ptr, instr_ptr, instr_count, stack_ptr
                        ),
                        NULL, true);
        
        ++instr_ptr;
        ++instr_count;
    }

    if (instr_ptr > instruction.len)
        throw_error(INSTR_OVERFLOW,
                    get_memory_snapshot(
                        data_ptr, instr_ptr, instr_count, stack_ptr
                    ),
                    NULL, true);
    
    if (options.verbose_txt)
        printf("\n------------------------------\n"
               "Stats\n"
               "* Number of instructions executed: %li\n", 
               instr_count);

    /* Wrap up */
    free_byte_arr(&data);
    free_byte_arr(&instruction);
    if (options.dump_mem)
        dump_memory_to_file();

    return 0;
}