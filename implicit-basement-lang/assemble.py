from assembler.tokenizer import tokenize
from assembler.token.scope_elem import ScopeStart, ScopeEnd
import assembler.parser as parser

import os
from math import log10


SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))


def main():
    file_name = f"{SCRIPT_DIR}/test/a.bs"
    with open(file_name, "r") as file:
        code = file.read() + chr(0)

    parse_result = tokenize(code)

    if isinstance(parse_result, tuple):
        output, struct_dict = parse_result

        divider = "=" * 80
        print("Parsed code:", divider, sep="\n")
        list_tokens(output)
        print("\n" + divider)

        rpn_tokens = parser.parse(output, struct_dict)
        list_tokens(rpn_tokens)
        print("\n" + divider)

    else:
        print("Error parsing")


def list_tokens(arr):
    indent = "    "
    indent_lvl = 1
    index_padding_len = (int(log10(len(arr))) + 1) if arr else 1
    for i, token in enumerate(arr):
        if isinstance(token, ScopeEnd):
            indent_lvl -= 1
        print(f"[{str(i).zfill(index_padding_len)}]{indent * indent_lvl}",
              end="")
        if isinstance(token, ScopeStart):
            indent_lvl += 1

        print(token)


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