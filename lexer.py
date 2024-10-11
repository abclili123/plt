import sys

def lexer(input_program):
    # first read in file
    try:
        with open(input_program, 'r') as program_body:
            output: list = []
            # read the file one character at a time
            while True:
                char = program_body.read(1)

                if not char:
                    break  # end of program

                if char == ' ': #white space delimits tokens
                    continue # move to next character

                # first try to match delimiters
                if char == '{':
                    output.append("OPENBRACK")
                    continue
                elif char == '}':
                    output.append("CLOSEBRACK")
                    continue
                elif char == '\n':
                    output.append("NEWLINE")
                    continue
                elif char == ',':
                    output.append("COMMA")
                    continue

                # then try to match keywords
                #define
                if char == 'd' or 'D':
                    char = program_body.read(1)
                    if char == 'e' or 'E':
                        char = program_body.read(1)
                        if char == 'f' or 'F':
                            char = program_body.read(1)
                            if char == 'i' or 'I':
                                char = program_body.read(1)
                                if char == 'n' or 'N':
                                    char = program_body.read(1)
                                    if char == 'e' or 'E':
                                        char = program_body.read(1)
                                        if char == ' ':
                                            output.append("KEYWORD (Value = \"define\")")
                                            continue
                # tempo

                # play

                # generate 
                # after getting generate you need to try matching a descirption literal , not an identifier

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

