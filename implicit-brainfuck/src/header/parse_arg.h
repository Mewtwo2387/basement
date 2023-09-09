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
extern bool opt_dump_memory;
extern bool opt_colored_output;
extern bool opt_verbose_output;
extern const char *opt_input_file_path;

void parse_cli_args(size_t argc, char *const argv[]);

#endif