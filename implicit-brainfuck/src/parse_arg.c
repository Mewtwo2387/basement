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

void print_help_msg(FILE *fp, const char *prog_name);

struct cli_options parse_cli_args(size_t argc, char *const argv[]) {
    struct  cli_options output = { 
        .dump_mem    = OPT_DUMP_MEM,
        .colored_txt = OPT_CLRD_TXT,
        .verbose_txt = OPT_VERB_TXT,
        .input_path  = NULL
    };

    opterr = 0;   // Custom error handling.
    char c;
    while ( (c = getopt(argc, argv, arg_options)) != -1 ) {
        switch (c) {
        case 'd':
            output.dump_mem = true;
            break;
        case 'c':
            output.colored_txt = true;
            break;
        case 'v':
            output.verbose_txt = true;
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
    output.input_path = argv[optind];

    return output;
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