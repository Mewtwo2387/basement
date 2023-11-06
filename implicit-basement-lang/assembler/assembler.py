import test_asm_code


def main():
    bytecode = test_asm_code.write_hello_word_asm()
    print(f"Hello World (unoptimized). size : {len(bytecode)} bytes")
    print_bytes(bytecode)
    with open("hello-world.o", "wb") as file:
        file.write(bytearray(bytecode))

    bytecode = test_asm_code.write_hello_word_optimized_asm()
    print(f"\nHello World (optimized). size : {len(bytecode)} bytes")
    print_bytes(bytecode)
    with open("hello-world-opt.o", "wb") as file:
        file.write(bytearray(bytecode))
    
    bytecode = test_asm_code.write_factorial_asm()
    print(f"\nFactorial function. size : {len(bytecode)} bytes")
    print_bytes(bytecode)
    with open("factorial.o", "wb") as file:
        file.write(bytearray(bytecode))


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