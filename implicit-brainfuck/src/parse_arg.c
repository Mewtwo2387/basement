#ifdef _WIN32
    #include "getopt-win32.h"
#else
    #define _POSIX_C_SOURCE 200809L
    #include <unistd.h>
#endif

#include <stdio.h>
#include <stdlib.h>
#include "parse_arg.h"

const char *arg_options = CLI_ARG_OPTIONS;

void print_help_msg(FILE *fp, const char *prog_name);

struct cli_options parse_cli_args(size_t argc, char *const argv[]) {
    struct  cli_options output = {
        .mem_size    = OPT_MEM_SIZE,
        .dump_mem    = OPT_DUMP_MEM,
        .colored_txt = OPT_CLRD_TXT,
        .verbose_txt = OPT_VERB_TXT,
        .input_path  = NULL
    };

    char *memsize_input = NULL;

    opterr = 0;   // Custom error handling.
    char c;
    while ( (c = getopt(argc, argv, arg_options)) != -1 ) {
        switch (c) {
        case 'm':
            memsize_input = optarg;
            break;
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
            if (c == 'm') {
                fprintf(stderr,
                        "Missing argument for option '-m'\n"
                        "Try running '%s -h' for more information\n",
                        argv[0]);
            } else {
                fprintf(stderr,
                        "Unknown option '-%c'\n"
                        "Try running '%s -h' for more information\n",
                        optopt, argv[0]);
            }
            exit(EXIT_FAILURE);
        }
    }

    if (optind >= argc) {
        fprintf(stderr,
                "No file input.\n"
                "Try running '%s -h' for help\n", argv[0]);
        exit(EXIT_FAILURE);
    }

    /* Assume that the non-option argument is the file path. */
    output.input_path = argv[optind];

    return output;
}

void print_help_msg(FILE *fp, const char *prog_name) {
    fprintf(fp, 
        "Usage: %s [OPTIONS...] file\n"
        "    file\n"
        "        Path to the input file.\n"
        "OPTIONS:\n"
        "    -m VALUE\n"
        "        Data memory size in KiB. See NOTES for more information.\n"
        "    -d\n"
        "        Dump the data and stack to 'datadump' and 'stackdump' in the\n"
        "        current directory.\n"
        "    -c\n"
        "        Add color through ANSI escape codes to the output texts\n"
        "        By default, the output texts have no color.\n"
        "    -v\n"
        "        Produce verbose output after evaluating the Brainfuck code.\n"
        "    -h\n"
        "        Print this help message and exit.\n\n"
        "NOTES:\n"
        "    Positive integer arguments for '-m' denotes the maximum data \n"
        "    memory size in KiB (kibibytes). A value of 1 KiB is equal to 1024\n"
        "    or 2^10 bytes.\n\n"
        "    A value of 0 for '-m' allocates the original data memory size of\n"
        "    vanilla Brainfuck interpreters which is 30,000 bytes.\n"
        "    This is also the default value of '-m'.\n\n"
        "    A value of -1 for '-m' allows the interpreter to allocate\n"
        "    indefinite amount of memory.\n"
        "    The interpreter shall then be in the 'YANFE!SMUG' mode.\n"
        "    Users are expected to exercise caution when in this mode.\n\n"
        "    No other negative integers are accepted for option '-m'.\n",
        prog_name
    );
}