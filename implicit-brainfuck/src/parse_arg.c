#ifdef _WIN32
    #include "getopt-win32.h"
#else
    #define _POSIX_C_SOURCE 200809L
    #include <unistd.h>
#endif

#include <stdio.h>
#include <stdlib.h>
#include "parse_arg.h"

const char *arg_options = "dcvh";

/* CLI option values */
bool opt_dump_memory = false;
bool opt_colored_output = false;
bool opt_verbose_output = false;
const char *opt_input_file_path = NULL;


void print_help_msg(FILE *fp, const char *prog_name);

void parse_cli_args(size_t argc, char *const argv[]) {
    opterr = 0;   // Custom error handling.
    char c;
    while ( (c = getopt(argc, argv, arg_options)) != -1 ) {
        switch (c) {
        case 'd':
            opt_dump_memory = true;
            break;
        case 'c':
            opt_colored_output = true;
            break;
        case 'v':
            opt_verbose_output = true;
            break;
        case 'h':
            print_help_msg(stdout, argv[0]);
            exit(EXIT_SUCCESS);
            break;
        default: // For the '?' output.
            fprintf(stderr,
                    "Unknown option '%c'\n"
                    "Try running '%s -h' for more information\n",
                    optopt, argv[0]);
            exit(EXIT_FAILURE);
        }
    }

    if (optind >= argc) {
        fprintf(stderr,
                "Missing an argument after the options.\n"
                "Try running '%s -h' for help\n", argv[0]);
        exit(EXIT_FAILURE);
    }

    /* Assume that the non-option argument is the file path. */
    opt_input_file_path = argv[optind];
}

void print_help_msg(FILE *fp, const char *prog_name) {
    fprintf(fp, 
        "Usage: %s [OPTIONS...] file\n\n"
        "OPTIONS:\n"
        "    file\n"
        "        Path to the file with the brainfuck code.\n"
        "    -d\n"
        "        Dump the data and stack to `datadump` and `stackdump` in the "
        "current directory.\n"
        "    -c\n"
        "        Add color through ANSI escape codes to the output texts\n"
        "        By default, the texts have no color.\n"
        "    -v\n"
        "        Produce verbose output after evaluating the brainfuck code.\n"
        "    -h\n"
        "        Print this help message and exit.\n",
        prog_name
    );
}