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

/* Pre-increment operator with wrap-around through modulo operation*/
#define PRE_INC_MOD(n, max) (n + 1) % max

#define MAX_MEMORY_SIZE 65536
#define MAX_STACK_SIZE 1024

const char *valid_char = "+-<>.,[]";

uint8_t  data[MAX_MEMORY_SIZE] = { '\0' };
string_t instruction;
size_t   stack[MAX_STACK_SIZE] = { (size_t)0 };

/* Pointers */
size_t data_ptr  = 0;
size_t instr_ptr = 0;
size_t stack_ptr = 0;

/* Command Line Options */
const char *dmpmem_cmd_short = "-d";
const char *dmpmem_cmd_long  = "--dump-mem";
const char *data_dump_name   = "datadump";
const char *stack_dump_name  = "stackdump";
bool to_dump_memory_to_file = false;

void dump_memory_to_file() {
    FILE *data_dump_fp, *stack_dump_fp;
    data_dump_fp = fopen(data_dump_name, "wb");
    stack_dump_fp = fopen(stack_dump_name, "wb");

    fwrite(data, sizeof(*data), MAX_MEMORY_SIZE, data_dump_fp);
    fwrite(stack, sizeof(*stack), MAX_STACK_SIZE, stack_dump_fp);

    fclose(data_dump_fp);
    fclose(stack_dump_fp);
}

struct memory get_memory_snapshot() {
    struct memory memory_snapshot = {
        .data=data,
        .data_size=MAX_MEMORY_SIZE,
        .data_ptr=data_ptr,

        .instruction=(&instruction),
        .instr_ptr=instr_ptr,

        .stack=stack,
        .stack_size=MAX_STACK_SIZE,
        .stack_ptr=stack_ptr
    };

    return memory_snapshot;
}

int main(size_t argc, const char* argv[]) {
    if (argc == 1) {
        fprintf(
            stderr,
            "no input file\n\n"
            "USAGE: %s INPUT-FILE [-d/--dump-mem]\n\n"
            "OPTIONS:\n"
            "    INPUT-FILE\n"
            "        Path to the input Brainfuck file.\n\n"
            "    -d, --dump-mem\n"
            "        Dump the contents of 'data' and 'stack' to "
            "files '%s' and '%s' respectively in the current directory.\n"
            "        By default, this is toggled off.\n",
            argv[0], data_dump_name, stack_dump_name
        );
        return 1;
    }

    FILE *input_file_ptr = fopen(argv[1], "r");
    if (input_file_ptr == NULL)
        throw_error(FILE_READ_FAILED, (struct memory){ 0 }, NULL, false);

    if (   argc >= 3
        && (
                   !strcmp(argv[2], dmpmem_cmd_short)
                || !strcmp(argv[2], dmpmem_cmd_long)
           )
    ) {
        to_dump_memory_to_file = true;            
    }

    init_string(&instruction);

    /* Read and filter out non-valid characters */
    char c;
    while ( fread(&c, 1, 1, input_file_ptr) ) {
        if ( strchr(valid_char, c) != NULL )
            string_append(&instruction, c);
    }

    fclose(input_file_ptr);

    /* Evaluate the program */
    while ( instr_ptr < instruction.len ) {
        if (instr_ptr >= instruction.len)
            throw_error(INSTR_OVERFLOW, get_memory_snapshot(), NULL, true);
        if (data_ptr >= MAX_MEMORY_SIZE)
            throw_error(DATA_OVERFLOW, get_memory_snapshot(), NULL, true);

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

                    instr_ptr = PRE_INC_MOD(instr_ptr, MAX_MEMORY_SIZE);
                    c = instruction.data[instr_ptr];
                }

                if (instr_ptr == instruction.len && bracket_lvl > 0)
                    throw_error(SYNTAX_ERROR, get_memory_snapshot(),
                                "Unbalanced brackets.", false);

            } else {
                if (stack_ptr == MAX_STACK_SIZE)
                    throw_error(STACK_OVERFLOW, get_memory_snapshot(), NULL,
                                true);

                stack[stack_ptr++] = instr_ptr;
            }
            break;
        case ']':
            if (stack_ptr == 0)
                throw_error(STACK_UNDERFLOW, get_memory_snapshot(), NULL, true);

            if (data[data_ptr] == 0)
                --stack_ptr;
            else
                instr_ptr = stack[stack_ptr - 1];

            break;
        default:
            throw_error(UNKNOWN, (struct memory){ 0 }, "Unknown instruction",
                        false);
        }
        instr_ptr = PRE_INC_MOD(instr_ptr, MAX_MEMORY_SIZE);
    }

    /* Wrap up */
    free_string(&instruction);
    if (to_dump_memory_to_file)
        dump_memory_to_file();

    return 0;
}