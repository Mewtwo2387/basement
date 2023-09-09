/******************************************************************************
            Yet ANother brainFuck intErpreter! (YANFE!)
                by: ImplicitNull (a.k.a. implicit none)

    A Brainfuck implementation. Pronounced as /yan.fei/. One thing to note here
    is that I set the memory size to 2^16 instead of the more common 30,000 to
    accomodate certain Brainfuck codes.

    Another version of YANFE! is in the works which uses dynamic arrays which
    can allocate indefinite amount of memory in a futile attempt to mimic the
    infinite memory of a Universal Turing Machine.

    Thanks to `Ei`, a fellow contributor, its agreed upon name is

        Yet ANother brainFuck intErpreter! - Super Memory Usage proGram
    or
        YANFE!SMUG

*******************************************************************************/

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <stdbool.h>

#include "string_type.h"
#include "memory_type.h"
#include "error.h"
#include "parse_arg.h"

/* Memory */
#define MAX_MEMORY_SIZE 65536
#define MAX_STACK_SIZE 1024

uint8_t  data[MAX_MEMORY_SIZE] = { '\0' };
string_t instruction;
size_t   stack[MAX_STACK_SIZE] = { (size_t)0 };

/* Dump file names */
const char *data_dump_name   = "datadump";
const char *stack_dump_name  = "stackdump";

#define VALID_BF_CHAR "+-<>.,[]"
#define DIVIDER "----------------------------------------"

void dump_memory_to_file() {
    FILE *data_dump_fp, *stack_dump_fp;
    data_dump_fp = fopen(data_dump_name, "wb");
    stack_dump_fp = fopen(stack_dump_name, "wb");

    fwrite(data, sizeof(*data), MAX_MEMORY_SIZE, data_dump_fp);
    fwrite(stack, sizeof(*stack), MAX_STACK_SIZE, stack_dump_fp);

    fclose(data_dump_fp);
    fclose(stack_dump_fp);
}

struct memory get_memory_snapshot(size_t data_ptr, size_t instr_ptr,
        size_t instr_count, size_t stack_ptr)
{
    struct memory memory_snapshot = {
        .data=data,
        .data_size=MAX_MEMORY_SIZE,
        .data_ptr=data_ptr,

        .instruction=(&instruction),
        .instr_ptr=instr_ptr,
        .instr_count=instr_count,

        .stack=stack,
        .stack_size=MAX_STACK_SIZE,
        .stack_ptr=stack_ptr
    };

    return memory_snapshot;
}

int main(size_t argc, char* const argv[]) {
    parse_cli_args(argc, argv);

    /* Read the input file */
    FILE *input_file_ptr = fopen(opt_input_file_path, "r");
    if (input_file_ptr == NULL) {
        char *add_err_msg = calloc(strlen(opt_input_file_path) + 15,
                                   sizeof(*add_err_msg));
        sprintf(add_err_msg, "Cannot read '%s'", opt_input_file_path);
        throw_error(FILE_READ_FAILED, (struct memory){ 0 }, add_err_msg, false,
                    opt_colored_output);
    }

    /* Load and filter out non-valid characters */
    init_string(&instruction);
    char c;
    while ( fread(&c, 1, 1, input_file_ptr) ) {
        if ( strchr(VALID_BF_CHAR, c) != NULL )
            string_append(&instruction, c);
    }

    fclose(input_file_ptr);

    /* Initialize pointers and counters */
    size_t data_ptr  = 0;
    size_t instr_ptr = 0;
    size_t stack_ptr = 0;
    size_t instr_count = 0;   // Count of all executed instructions

    /* Evaluate the program */
    while ( instr_ptr < instruction.len ) {
        switch ( (c = instruction.data[instr_ptr]) ) {
        case '+':
            ++data[data_ptr];
            break;
        case '-':
            --data[data_ptr];
            break;
        case '>':
            ++data_ptr;
            break;
        case '<':
            --data_ptr;
            break;
        case '.':
            putc(data[data_ptr], stdout);
            break;
        case ',':
            data[data_ptr] = getc(stdin);
            break;
        case '[':
            if (data[data_ptr] == 0) {
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
                               "Unbalanced brackets.", 
                               false, opt_colored_output);

            } else {
                if (stack_ptr == MAX_STACK_SIZE)
                    throw_error(STACK_OVERFLOW,
                                get_memory_snapshot(
                                    data_ptr, instr_ptr, instr_count, stack_ptr
                                ),
                                NULL, true, opt_colored_output);

                stack[stack_ptr++] = instr_ptr;
            }
            break;
        case ']':
            if (stack_ptr == 0)
                throw_error(STACK_UNDERFLOW,
                            get_memory_snapshot(
                                data_ptr, instr_ptr, instr_count, stack_ptr
                            ),
                            NULL, true, opt_colored_output);

            if (data[data_ptr] == 0)
                --stack_ptr;
            else
                instr_ptr = stack[stack_ptr - 1];

            break;
        default:
            throw_error(UNKNOWN, (struct memory){ 0 }, "Unknown instruction",
                        false, opt_colored_output);
        }

        // Check for invalid data pointer values
        if (data_ptr == SIZE_MAX)
            throw_error(DATA_UNDERFLOW,
                        get_memory_snapshot(
                            data_ptr, instr_ptr, instr_count, stack_ptr
                        ),
                        NULL, true, opt_colored_output);
        if (data_ptr >= MAX_MEMORY_SIZE)
            throw_error(DATA_OVERFLOW,
                        get_memory_snapshot(
                            data_ptr, instr_ptr, instr_count, stack_ptr
                        ),
                        NULL, true, opt_colored_output);
        
        ++instr_ptr;
        ++instr_count;
    }

    if (instr_ptr > instruction.len)
        throw_error(INSTR_OVERFLOW,
                    get_memory_snapshot(
                        data_ptr, instr_ptr, instr_count, stack_ptr
                    ),
                    NULL, true, opt_colored_output);
    
    if (opt_verbose_output)
        printf("\n%s\nStats\n * Number of instructions executed: %li\n", 
               DIVIDER, instr_count);

    /* Wrap up */
    free_string(&instruction);
    if (opt_dump_memory)
        dump_memory_to_file();

    return 0;
}