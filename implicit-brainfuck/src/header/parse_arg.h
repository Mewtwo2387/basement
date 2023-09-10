#ifndef PARSE_ARG_H
#define PARSE_ARG_H

#include <stdbool.h>
#include <stddef.h>

/*
    OPTIONS:
        file
            Path to the file with the brainfuck code.
        -d
            Dump the data and stack to 'datadump' and 'stackdump' in the
            current directory.
        -c
            Add color with ANSI codes to the output and error messages.
            By default, the output texts have no color.
        -v
            Produce verbose output after evaluating the code.
        -h
            Print the help message and exit.
*/
extern const char *arg_options;

/* CLI argument options */
struct cli_options {
    bool dump_mem;
    bool colored_txt;
    bool verbose_txt;
    const char *input_path;
};

/* CLI argument default values */
#define OPT_DUMP_MEM false
#define OPT_CLRD_TXT false
#define OPT_VERB_TXT false

struct cli_options parse_cli_args(size_t argc, char *const argv[]);

#endif