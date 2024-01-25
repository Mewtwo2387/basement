from assembler.parser import parse

def main():
    code = """
        function my_func() => i32:
            return 0;
        end function
    """ + chr(0)
    res = parse(code)
    if isinstance(res, tuple):
        output, _ = res
        print(*output, sep=", ")
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