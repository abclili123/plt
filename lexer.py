import sys

def lexer(input_program):
    # first read in file
    try:
        with open(input_program, 'r') as program_body:
            # read the file one word at a time
            for line in program_body:
                for token in line:
                    # make sure the word is split correctly
                    # for example, a token cannot have {, }, or , at the end
                    # so seperate out the delimiters

                    # first try to match delimiters

                    # then try to match keywords

                    # then try to match types

                    # then try to match literals (i think in the order of the grammar)

                    # catch any errors
                    pass

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

