#ifdef _WIN32
    #include "getopt-win32.h"
#else
    #define _POSIX_C_SOURCE 200809L
    #include <unistd.h>
#endif

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <errno.h>
#include <stdint.h>
#include "parse_arg.h"

const char *arg_options = CLI_ARG_OPTIONS;

#define HELP_SUGGESTION_STR "Try running '%s -h' for more information\n"

void print_help_msg(FILE *fp, const char *prog_name);

struct cli_options parse_cli_args(size_t argc, char *const argv[]) {
    struct  cli_options output = {
        .mem_size    = OPT_MEM_SIZE,
        .dump_mem    = OPT_DUMP_MEM,
        .colored_txt = OPT_CLRD_TXT,
        .verbose_txt = OPT_VERB_TXT,
        .input_path  = NULL
    };

    opterr = 0;   // Custom error handling.
    errno = 0;
    char c;
    while ( (c = getopt(argc, argv, arg_options)) != -1 ) {
        switch (c) {
        case 'm':
            char *end_ptr;
            long int m_opt_arg = strtol(optarg, &end_ptr, 10);

            if (strlen(end_ptr) > 0) {
                fprintf(stderr,
                        "'%s' is invalid argument for '-m'. "
                        "Must be a base-10 integer\n"
                        HELP_SUGGESTION_STR,
                        optarg, argv[0]);
                exit(EXIT_FAILURE);
            }
            if (errno == ERANGE) {
                fprintf(stderr,
                        "'%s' exceeds the 32 bit signed integer limit", optarg);
                exit(EXIT_FAILURE);
            }

            /* Convert the passed argument to the corresponding memory size */
            if (m_opt_arg == 0) {
                output.mem_size = OPT_MEM_SIZE;
            } else if (m_opt_arg == -1) {
                output.mem_size = 0;   // The client function will handle this
            } else if (m_opt_arg > 0) {
                output.mem_size = m_opt_arg;
            } else {
                fprintf(stderr,
                        "'%ld' is an invalid argument for '-m'. Must be >= -1\n"
                        HELP_SUGGESTION_STR,
                        m_opt_arg, argv[0]);
                exit(EXIT_FAILURE);
            }
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
                        HELP_SUGGESTION_STR,
                        argv[0]);
            } else {
                fprintf(stderr,
                        "Unknown option '-%c'\n"
                        HELP_SUGGESTION_STR,
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
        "        Data memory size in bytes. See NOTES for more information.\n"
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
        "    memory size in bytes.\n\n"
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