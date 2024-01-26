from assembler.parser import parse
import assembler.token.delim as tokdelim

def main():
    code = """
        function my_func(i8 x, i8 y) => i8:
            # Comment here
        end function
    """ + chr(0)
    res = parse(code)
    if isinstance(res, tuple):
        output, _ = res

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