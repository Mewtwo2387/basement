#ifndef PARSE_ARG_H
#define PARSE_ARG_H

#include <stdbool.h>
#include <stddef.h>

/*
    Usage: brainfuck [OPTIONS...] file
        file
            Path to the input file.
    OPTIONS:
        -m VALUE
            Data memory size in KiB. See NOTES below for the available options.
        -d
            Dump the data and stack to 'datadump' and 'stackdump' in the
            current directory.
        -c
            Add color with ANSI escape codes to the output texts.
            By default, the output texts have no color.
        -v
            Produce verbose output after evaluating the Brainfuck code.
        -h
            Print the help message and exit.
    
    NOTES:
        Positive integer arguments for `-m` denotes the maximum data memory size
        in KiB (kibibytes). A value of 1 KiB is equal to 1024 or 2^10 bytes.

        A value of 0 for `-m` allocates the original data memory size of vanilla
        Brainfuck interpreters which is 30,000 bytes. This is also the default
        value for this option.

        A value of -1 for `-m` allows the interpreter to allocate
        indefinite amount of data memory.
        The interpreter shall then be in the 'YANFE!SMUG' mode.
        Users are expected to exercise caution when in this mode.

        No other negative integers are accepted for the option '-m'
*/

/* CLI options*/
#define CLI_ARG_OPTIONS "m:dcvh"

/* CLI argument options */
struct cli_options {
    size_t mem_size;
    bool dump_mem;
    bool colored_txt;
    bool verbose_txt;
    const char *input_path;
};

/* CLI argument default values */
#define OPT_MEM_SIZE 30000
#define OPT_DUMP_MEM false
#define OPT_CLRD_TXT false
#define OPT_VERB_TXT false

struct cli_options parse_cli_args(size_t argc, char *const argv[]);

#endif