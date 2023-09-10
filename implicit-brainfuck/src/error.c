#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "error.h"

/*  ANSI Color codes
    Source:
        https://gist.github.com/RabaDabaDoba/145049536f815903c79944599c6f952a
*/ 
#define ANSI_RED_BOLD    "\e[1;31m"
#define ANSI_GRN         "\e[0;32m"
#define ANSI_GRN_BOLD    "\e[1;32m"
#define COLOR_RESET      "\e[0m"

#define PRINT_COLORED_DESC(str)                 \
    fprintf(stderr, "%s" str "%s",              \
            (colored_error_msg)? ANSI_GRN : "", \
            (colored_error_msg)? COLOR_RESET : "")

#define PRINT_DESC_VALUE(fmt, value)                        \
    fprintf(stderr, "%s" fmt "%s",                          \
            (colored_error_msg)? ANSI_GRN_BOLD : "", value, \
            (colored_error_msg)? COLOR_RESET : "")

const char *divider = 
    "===================="
    "===================="
    "===================="
    "====================";

/* Flag for colored messages. The client will have to set this. */
bool colored_error_msg = false;


static void print_memory(uint8_t *arr, size_t size, size_t pos, int loffset,
                         int roffset)
{
    /* Print the data sequence */
    for (int i = loffset; i < roffset; ++i) {
        /* NOTE: Very hacky. Instead of checking whether substracting `pos`
                 underflows, we allow it to underflow wrapping its value to the
                 highest possible values which SHOULD be greater than `size`,
                 the array size.
        */ 
        if ((pos + i) < size)
            fprintf(stderr, "%3.3i ", arr[pos + i]);
        else
            fprintf(stderr, "??? ");
    }
    fprintf(stderr, "\n");

    /* Print the position indicator and ruler pointers*/
    for (int i = loffset; i < roffset; ++i) {
        if ( (i == loffset && i != 0) || (i == (roffset - 1)) )
            fprintf(stderr, "|   ");
        else if (i == 0)
            fprintf(stderr, "^^^ ");
        else
            fprintf(stderr, "    ");    // 4 spaces
    }
    fprintf(stderr, "\n");

    /* Print a ruler */
    for (int i = loffset; i < roffset; ++i) {
        if (i == loffset)
            fprintf(stderr, "@%-5i", (int32_t)(pos + i));
        else if (i == (roffset - 1))
            fprintf(stderr, "@%-5i", (int32_t)(pos + i));
        else if (i == (loffset + 1))
            fprintf(stderr, "  ");   // 2 spaces
        else
            fprintf(stderr, "    ");    // 4 spaces
    }
    fprintf(stderr, "\n");
}

static void print_instruction(char *instruction, size_t instr_size, size_t pos,
                              int loffset, int roffset)
{
    int32_t lbound = pos + loffset;
    int32_t ubound = pos + roffset + 1;

    if (lbound < 0)
        lbound = 0;
    if (ubound > instr_size)
        ubound = instr_size;

    /* Print the instructions */
    for (int32_t i = lbound; i < ubound; ++i)
        fprintf(stderr, "%c", instruction[i]);
    fprintf(stderr, "\n");

    /* Print the position indicator and ruler pointers*/
    for (int32_t i = lbound; i < ubound; ++i) {
        if ( (i == lbound || i == (ubound - 1)) && i != pos)
            fprintf(stderr, "|");
        else if (i == pos)
            fprintf(stderr, "^");
        else
            fprintf(stderr, " ");
    }
    fprintf(stderr, "\n");

    /* Print the ruler */
    for (int32_t i = lbound; i < ubound; ++i) {
        if (i == lbound || i == (ubound - 1))
            fprintf(stderr, "@%-4i", i);
        else if (i > (lbound + 4))
            fprintf(stderr, " ");
    }
    fprintf(stderr, "\n");
}


void throw_error(
    enum ERROR_TYPE error_type,
    struct memory mem_snapshot,
    char *add_msg,
    bool to_print_memory)
{
    /* Flush stdout for any queued texts */
    fflush(stdout);

    fprintf(stderr, "%sERROR: ", ((colored_error_msg)? ANSI_RED_BOLD : ""));

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
    case UNKNOWN_INSTR:
        fprintf(stderr, "Unknown instruction\n");
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
    if (colored_error_msg)
        fprintf(stderr, COLOR_RESET);

    /* Print the additional error message */
    if (error_type != CUSTOM && add_msg != NULL && strlen(add_msg) > 0)
        fprintf(stderr, "%s\n", add_msg);

    if (!to_print_memory)
        exit(EXIT_FAILURE);
    
    /* Print the program data around the current data pointer */
    fprintf(stderr, "%s\n", divider);
    PRINT_COLORED_DESC("Data pointer: ");
    PRINT_DESC_VALUE("@%lu\n", mem_snapshot.data_ptr);
    print_memory(mem_snapshot.data, mem_snapshot.data_size,
                 mem_snapshot.data_ptr, -8, 8);

    /* Print the instruction around the current instruction pointer */
    // TODO: ADD COLORS TO THE DESCRIPTION
    fprintf(stderr, "%s\n", divider);
    PRINT_COLORED_DESC("Instruction pointer: ");
    PRINT_DESC_VALUE("@%lu, ", mem_snapshot.instr_ptr);
    PRINT_COLORED_DESC("Number of instructions executed: ");
    PRINT_DESC_VALUE("%lu\n", mem_snapshot.instr_count);


    print_instruction(mem_snapshot.instruction, mem_snapshot.instr_size,
                      mem_snapshot.instr_ptr, -8, 8);

    /* Print the stack */
    fprintf(stderr, "%s\nStack:\n", divider);
    if (mem_snapshot.stack_ptr > 0) {
        for (size_t i = mem_snapshot.stack_ptr; i > 0; --i) {
            fprintf(stderr, "#%2.2ld   %3.3ld\n", i - 1,
                    mem_snapshot.stack[i - 1]);
        }
    }

    exit(EXIT_FAILURE);
}