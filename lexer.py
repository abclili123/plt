import sys

######## KEYWORDS ########
KEYWORDS = [
    "define",
    "tempo",
    "play",
    "generate",
]
##########################



def match_types():
    print("TODO: match types not yet implemented")

def match_literals():
    print("TODO: match literals not yet implemented")

def generate_literals():
    print("TODO: generate literals not yet implemented")

def handle_errors():
    print("TODO: handle errors not yet implemented")

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

                #####
                # something we can do is have a list of keywords
                # and then iterate through the list and check if the characters match
                # and then we dont have to write out each one manually
                # but we can do that later because we are just trying to get the basic functionality working
                #####

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
                
                if char.lower() == 't':
                    char = program_body.read(1)
                    if char.lower() == 'e':
                        char = program_body.read(1)
                        if char.lower() == 'm':
                            char = program_body.read(1)
                            if char.lower() == 'p':
                                char = program_body.read(1)
                                if char.lower() == 'o':
                                    char = program_body.read(1)
                                    if char == ' ':
                                        output.append("KEYWORD (Value = \"tempo\")")
                                        continue                        


                # play

                if char.lower() == 'p':
                    char = program_body.read(1)
                    if char.lower() == 'l':
                        char = program_body.read(1)
                        if char.lower() == 'a':
                            char = program_body.read(1)
                            if char.lower() == 'y':
                                char = program_body.read(1)
                                if char == ' ':
                                    output.append("KEYWORD (Value = \"play\")")
                                    continue

                # generate
                if char.lower() == 'g':
                    char = program_body.read(1)
                    if char.lower() == 'e':
                        char = program_body.read(1)
                        if char.lower() == 'n':
                            char = program_body.read(1)
                            if char.lower() == 'e':
                                char = program_body.read(1)
                                if char.lower() == 'r':
                                    char = program_body.read(1)
                                    if char.lower() == 'a':
                                        char = program_body.read(1)
                                        if char.lower() == 't':
                                            char = program_body.read(1)
                                            if char.lower() == 'e':
                                                char = program_body.read(1)
                                                if char == ' ':
                                                    output.append("KEYWORD (Value = \"generate\")")
                                                    continue
                # after getting generate you need to try matching a descirption literal , not an identifier
                generate_literals()
                # then try to match types
                match_types()
                # then try to match literals (i think in the order of the grammar)
                match_literals()
                # catch any errors
                handle_errors()

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

