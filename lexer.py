import sys

def lexer(input_program):
    # first read in file
    try:
        with open(input_program, 'r') as program_body:
            # read the file one character at a time
            while True:
                char = program_body.read(1)  # Read one character at a time
                if not char:
                    break  # End of program
                # first try to match delimiters

                # then try to match keywords

                # then try to match types

                # then try to match literals (i think in the order of the grammar)

                # catch any errors

    except FileNotFoundError:
        print(f"Error: The program '{filename}' was not found.")
    except Exception as e:
        print(f"Error reading file: {e}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python lexer.py <filename>")
    else:
        filename = sys.argv[1]
        lexer(filename)

