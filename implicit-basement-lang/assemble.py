import os

from assembler.parser import parse
import assembler.token.delim as tokdelim


SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))


def main():
    file_name = f"{SCRIPT_DIR}/test/a.bs"
    with open(file_name, "r") as file:
        code = file.read() + chr(0)

    parse_result = parse(code)

    if isinstance(parse_result, tuple):
        output, _ = parse_result

        indent = "    "
        print("Parsed code:", "=" * 80, sep="\n")

        indent_lvl = 1
        to_indent = True
        for token in output:
            if to_indent:
                print(indent * indent_lvl, sep="", end="")

            to_indent = False
            match token:
                case tokdelim.ScopeStart():
                    print("\n", indent * indent_lvl, token, sep="", end="")
                    indent_lvl += 1
                    print("\n", indent * indent_lvl, sep="", end="")
                case tokdelim.ScopeEnd():
                    indent_lvl -= 1
                    print(f"{chr(27)}[100D", indent * indent_lvl, token, sep="")
                    to_indent = True
                case tokdelim.EndOfLine():
                    print(token)
                    to_indent = True
                case _:
                    print(token, end=", ")
        print("\n" + "=" * 80)
    else:
        print("Error parsing")


def print_bytes(arr):
    print("  |", *[f"{i:02x}" for i in range(16)], sep=" ",
          end=("\n" + "---"*(17)))
    for i, b in enumerate(arr):
        if (i % 16 == 0):
            print(f"\n{i:02x}| ", end="")
        print(f"{b:02x} ", end="")
    print("\n")


if __name__ == "__main__":
    main()