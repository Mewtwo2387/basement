import argparse


def decompose(n):
    a = int(n ** 0.5)
    return a, n // a, n % a


def int_to_bf_code(n, at_start=False):
    if n == 0:
        return "."

    instr_char = "+" if (n > 0) else "-"
    a, b, c = decompose(abs(n))
    bf_code = f"{'+' * a}[>{instr_char * b}<-]>{instr_char * c}."
    if not at_start:
        bf_code = "<" + bf_code
    return bf_code


def relative_pos(string):
    ascii_val = list(map(ord, string))
    return [right - left for left, right in zip(ascii_val[:-1], ascii_val[1:])]


def parse_cli_arguments():
    parser = argparse.ArgumentParser(
        description="Generate Brainfuck code that prints a specified text"
    )
    input_group = parser.add_mutually_exclusive_group()
    input_group.add_argument("-i", "--input", action="store",
                             help="Input file containing the text to be "
                                  "converted")
    input_group.add_argument("-t", "--text", action="store",
                             help="Convert the input text to brainfuck code")

    parser.add_argument("-o", "--output", action="store", default="output.bf",
                             help="Path to the file to write the code to")
    parser.add_argument("-n", "--new-line", action="store_true",
                        help="Add a trailing new line")
    return parser.parse_args()


def main():
    args = parse_cli_arguments()

    if (args.input is None):
        string = args.text + ("\n" if (args.new_line) else "")
    else:
        string = ""
        with open(args.input, "r") as file:
            string = file.read()


    diff = relative_pos(string)
    bf_code = "".join([
        int_to_bf_code(ord(string[0]), at_start=True),
        *[int_to_bf_code(d, at_start=False) for d in diff]
    ])
    
    with open(args.output, "w") as file:
        file.write(bf_code)


if __name__ == "__main__":
    main()