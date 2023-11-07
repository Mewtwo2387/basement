#include <stdio.h>
#include <stdlib.h>
#include "cpu.h"

int main(size_t argc, char *argv[]) {
    int main_ret_val = 0;

    /* Get the program */
    uint8_t *program = malloc(sizeof(*program) * MEM_SIZE_DEFAULT);
    if (argc != 2) {
        fprintf(
            stderr,
            "Error: \"%s\" accepts 1 argument, the path to input file.\n",
            argv[0]
        );
        exit(EXIT_FAILURE);
    }

    FILE *fptr;
    if ( (fptr = fopen(argv[1], "rb")) == NULL ) {
        fprintf(stderr, "Error: Invalid input file: \"%s\"\n", argv[1]);
        exit(EXIT_FAILURE);
    }

    size_t prog_size = 0;
    uint8_t byte;
    while (fread(&byte, sizeof(byte), 1, fptr)) {
        if (prog_size >= MEM_SIZE_DEFAULT) {
            fprintf(
                stderr,
                "Error: Input file exceeds the maximum buffer size (%d)\n",
                MEM_SIZE_DEFAULT
            );
            exit(EXIT_FAILURE);
        }
        program[prog_size++] = byte;
    }

    /* Shave off the unused bytes in the program array */
    program = realloc(program, prog_size);

    CPU_t cpu;
    init_cpu(&cpu, MEM_SIZE_DEFAULT, STACK_SIZE_DEFAULT);
    cpu_load_program(&cpu, program, prog_size);
    
    cpu_run(&cpu);
    if (cpu.state == STATE_HALT_FAILURE) {
        fprintf(stderr, "VM failed: %s\n", cpu.state_msg);
        main_ret_val = 1;
    }

    free_cpu(&cpu);
    free(program);
    return main_ret_val;
}