import sys
import re

######## TOKENS ########
TOKENS = [
    ('KEYWORD', r'\b(tempo|define|loop|instrument|note|beat)\b'),
    ('IDENTIFIER', r'[a-zA-Z_][a-zA-Z0-9_]*'),
    ('NUMBER', r'\d+'),
    ('OPENBRACK', r'\{'),
    ('CLOSEBRACK', r'\}'),
    ('NEWLINE', r'\n'),
    ('WHITESPACE', r'\s+'),
    ('COMMA', r','),
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

def write_output_to_file(output):
    with open("output.txt", "w") as output_file:
            for token in output:
                output_file.write(token + "\n")
    print("Output written to output.txt")

def lexer(input_program):
    # first read in file
    try:
        with open(input_program, 'r') as program_body:
            output = []
            # this is basically just reading entire program
            # as string, then parsing it character by character
            program_file = program_body.read()
            cursor = 0
            
            # move cursor until EOF
            while cursor < len(program_file):
                matched = False
                for token_name, token_pattern in TOKENS:
                    # use re to match regex patterns in file
                    match = re.match(token_pattern, program_file[cursor:])
                    if match:
                        # append token to output
                        matched = True
                        if token_name != 'WHITESPACE' and token_name != 'NEWLINE':
                                output.append(f"< {token_name} , {match.group()} >")
                        elif token_name == 'NEWLINE':
                            output.append(f"< {token_name} >")
                        
                        # adjust pointer to end of last found token
                        cursor += match.end()
                        break
                
                if not matched:
                    # here we should also do finer error checking
                    # for example, if a found token is not in grammar but
                    # close due to spelling error, like loopf or tempo1, 
                    # we should throw an error with edit suggestion
                    output.append(f"ERROR: Unexpected character '{program_file[cursor]}'")
                    cursor += 1
                

                
                # after getting generate you need to try matching a descirption literal , not an identifier
                # generate_literals()
                # then try to match types
                # match_types()
                # then try to match literals (i think in the order of the grammar)
                # match_literals()
                # catch any errors
                # handle_errors()
        
        write_output_to_file(output)
       

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

