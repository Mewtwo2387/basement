#include <stdio.h>
#include <stdlib.h>
#include "cpu.h"

void print_bytes(uint8_t *bytes, size_t bytes_size);

int main(size_t argc, char *argv[]) {
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

    print_bytes(program, prog_size);

    CPU_t cpu;
    init_cpu(&cpu, MEM_SIZE_DEFAULT);
    cpu_load_program(&cpu, program, prog_size);
    
    cpu_run(&cpu);
    if (cpu.state == HALT_FAILED)
        fprintf(stderr, "VM failed: %s\n", cpu.state_msg);

    free_cpu(&cpu);
    free(program);
    return 0;
}

void print_bytes(uint8_t *bytes, size_t bytes_size) {    
    /* Print header */
    printf("    ");
    for (size_t i = 0x00; i < 0x10; ++i)
        printf("%2.2lx ", i);
    printf("\n");

    printf("00| ");
    for (size_t i = 0; i < bytes_size; ++i) {
        if (i % 16 == 0)
            printf("\n%2.2lx| ", i);
        printf("%2.2x ", bytes[i]);
    }
    printf("\n\n");
}