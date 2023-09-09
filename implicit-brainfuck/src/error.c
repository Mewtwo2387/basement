#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "error.h"

/*  ANSI Color codes
    Source:
        https://gist.github.com/RabaDabaDoba/145049536f815903c79944599c6f952a
*/ 
#define ANSI_RED "\e[0;31m"
#define COLOR_RESET "\e[0m"

const char *divider = 
    "===================="
    "===================="
    "===================="
    "====================";


static void print_memory(uint8_t *arr, size_t size, size_t pos, int loffset,
        int roffset, bool datum_as_char) {
    /* Print the data sequence */
    for (int i = loffset; i < roffset; ++i) {
        /* NOTE: Very hacky. Instead of checking whether substracting `pos`
                 underflows, we allow it to underflow wrapping its value to the
                 highest possible values which SHOULD be greater than `size`,
                 the array size.
        */ 
        if ((pos + i) < size)
            fprintf(stderr, (datum_as_char)? "%c " : "%3.3i ", arr[pos + i]);
        else if (!datum_as_char)
            fprintf(stderr, "??? ");
    }
    fprintf(stderr, "\n");

    /* Print the position indicator */
    for (int i = loffset; i < roffset; ++i) {
        if (i == 0) {
            fprintf(stderr, (datum_as_char)? "^ " : "^^^ ");
        } else {
            if ((pos + i) < size)
                fprintf(stderr, (datum_as_char)? "  " : "    ");
            else if (!datum_as_char)
                fprintf(stderr, "    ");
        }
    }
    fprintf(stderr, "\n");
}

void throw_error(
    enum ERROR_TYPE error_type,
    struct memory mem_snapshot,
    char *add_msg,
    bool to_print_memory,
    bool colored_txt)
{
    fprintf(stderr, "%sERROR: ", ((colored_txt)? ANSI_RED : ""));

    switch (error_type) {
    case FILE_READ_FAILED:
        fprintf(stderr, "File read error\n");
        break;
    case INSTR_OVERFLOW:
        fprintf(stderr, "Instruction buffer overflow\n");
        break;
    case INSTR_UNDERFLOW:
        fprintf(stderr, "Instruction buffer underflow\n");
        break;
    case DATA_OVERFLOW:
        fprintf(stderr, "Data buffer overflow\n");
        break;
    case DATA_UNDERFLOW:
        fprintf(stderr, "Data buffer underflow\n");
        break;
    case STACK_OVERFLOW:
        fprintf(stderr, "Stack buffer overflow\n");
        break;
    case STACK_UNDERFLOW:
        fprintf(stderr, "Stack buffer underflow\n");
        break;
    case SYNTAX_ERROR:
        fprintf(stderr, "Syntax error\n");
        break;
    case UNKNOWN:
        fprintf(stderr, "Unknown error\n");
        break;
    case CUSTOM:
        if (add_msg == NULL) {
            fprintf(stderr, "<Internal error: custom error unspecified>");
            exit(EXIT_FAILURE);
        }
        fprintf(stderr, "%s\n", add_msg);
        break;
    default:
        fprintf(stderr, "<Internal error: Unknown error type>\n");
        exit(EXIT_FAILURE);
    }
    
    /* Reset color */  
    if (colored_txt)
        fprintf(stderr, COLOR_RESET);

    /* Print the additional error message */
    if (error_type != CUSTOM && add_msg != NULL && strlen(add_msg) > 0)
        fprintf(stderr, "%s\n", add_msg);

    if (!to_print_memory)
        exit(EXIT_FAILURE);
    
    /* Print the program data around the current data pointer */
    fprintf(stderr, "%s\nData pointer @%lu\n", divider, mem_snapshot.data_ptr);
    print_memory(mem_snapshot.data, mem_snapshot.data_size,
                 mem_snapshot.data_ptr, -8, 8, false);

    /* Print the instruction around the current instruction pointer */
    fprintf(stderr, "%s\nInstruction pointer @%lu\n",
            divider, mem_snapshot.instr_ptr);
    print_memory(mem_snapshot.instruction->data, mem_snapshot.instruction->len,
                 mem_snapshot.instr_ptr, -8, 8, true);

    /* Print the stack */
    fprintf(stderr, "%s\nStack:\n", divider);
    if (mem_snapshot.stack_ptr > 0) {
        for (size_t i = mem_snapshot.stack_ptr; i > 0; --i) {
            fprintf(stderr, "#%2.2ld   %3.3ld\n", i - 1,
                    mem_snapshot.stack[i - 1]);
        }
    }

    // Take care of the "instruction" string JUST to be sure.
    free_string(mem_snapshot.instruction);
    exit(EXIT_FAILURE);
}