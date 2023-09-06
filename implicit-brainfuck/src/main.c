/*
    AUTHOR: ImplicitNull

    A Brainfuck implementation. I have set the memory size to 1024, but it
    could be increased since the original description calls for "infinite"
    memory.

    NOTE: THIS SHIT IS NOT YET TESTED. COMPILE AT YOUR RISK.
            IF THIS BRICKS YOUR PC, THAT AINT MY FAULT.
*/

#include <stdio.h>
#include <stddef.h>
#include <stdlib.h>
#include <string.h>

#include "string_type.h"

#define MAX_MEMORY_SIZE 1024
#define MAX_STACK_SIZE 1024

const char *valid_char = "+-<>.,[]";

char data[MAX_MEMORY_SIZE] = { '\0' };
string_t instruction;
size_t stack[MAX_STACK_SIZE] = { (size_t)0 };

/* Pointers */
size_t data_ptr  = 0;
size_t instr_ptr = 0;
size_t stack_ptr = 0;

void graceful_exit(int ret_code) {
    free_string(&instruction);
    exit(ret_code);
}

int main(size_t argc, const char* argv[]) {
    if (argc == 1) {
        fprintf(stderr, "help yourself :yanfeismug:\n");
        return 1;
    }

    FILE *input_file_ptr = fopen(argv[1], "r");
    if (input_file_ptr == NULL) {
        fprintf(stderr, "cant read this shit: \"%s\"\n", argv[1]);
        return 1;
    }

    init_string(&instruction);

    /* Read and filter out non-valid characters */
    char c;
    while ( fread(&c, 1, 1, input_file_ptr) ) {
        if ( strchr(valid_char, c) != NULL ) {
            string_append(&instruction, c);
        }
    }

    fclose(input_file_ptr);

    /* Evaluate the program */
    while ( instr_ptr < instruction.len ) {
        c = instruction.data[instr_ptr];

        /* Stack manipulating instructions */
        switch (c) {
        case '[':
            if (data[data_ptr] == 0) {
                // Skip the entire loop if 0
                int bracket_lvl = 1;
                while (instr_ptr < instruction.len && bracket_lvl > 0) {
                    c = instruction.data[++instr_ptr];
                    if (c == '[')
                        ++bracket_lvl;
                    if (c == ']')
                        --bracket_lvl;
                }
                if (instr_ptr == instruction.len && bracket_lvl > 0) {
                    fprintf(stderr, "mismatched bracket pairs!\n");
                    graceful_exit(1);
                }
            } else {
                if (stack_ptr == MAX_STACK_SIZE) {
                    fprintf(stderr, "stack overflow!\n");
                    graceful_exit(1);
                }
                stack[stack_ptr++] = ++instr_ptr;
            }
            continue;
        case ']':
            if (data[data_ptr] == 0) {
                ++instr_ptr;
            } else {
                if (stack_ptr == 0) {
                    fprintf(stderr, "stack underflow!\n");
                    graceful_exit(1);
                }
                instr_ptr = stack[stack_ptr - 1];
            }
            continue;
        }

        /* Data manipulating instructions */
        switch (c) {
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
        default:
            fprintf(stderr, "you fucking broke it, didnt ya?\n");
            graceful_exit(1);
        }
        ++instr_ptr;
    }

    free_string(&instruction);
    return 0;
}