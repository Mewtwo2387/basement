from assembler.tokenizer import tokenize
from assembler.token.function import Function
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

        rpn_tokens = parser.parse(output)
        list_tokens(rpn_tokens)
        print("\n" + divider)

        print("Structs:")
        for name, struct_obj in struct_dict.items():
            print(f"\t{name}:")
            for field, field_size in struct_obj.fields.items():
                print(f"\t\t{field}: {field_size} byte(s)")
            print(f"\t(Total byte size: {struct_obj})")
        print("\n" + divider)

        print("Functions:")
        if rpn_tokens is not None:
            for token in rpn_tokens:
                if not isinstance(token, Function):
                    continue
                print(f"\t{token.name} => {token.ret_type} byte(s):")
                for var_name, var_obj in token.local_var_dict.items():
                    print(f"\t\t{var_name}: {var_obj.size} byte(s)")
                print(f"\t(Total byte size: {token.size})")

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