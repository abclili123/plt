import sys

######## KEYWORDS ########
KEYWORDS = [
    "define",
    "tempo",
    "play",
    "generate",
    "loop",
    "instrument",
    "note",
    "beat",
]
##########################

#### INSTRUMENT TYPES ####
# important to have these separate from keywords for generate stage
INSTRUMENTS = [
        "piano",
        "guitar", 
        "horn",
        "bass",
        "snare",
        "hihat"
    ]
##########################

def handle_error(buffer):
    print(f"Error: Unrecognized token '{buffer}'")


#### MATCHING FUNCTIONS ####
def match_delimiter(char):
    if char == '{':
        return "OPENBRACK"
    elif char == '}':
        return "CLOSEBRACK"
    elif char == '\n':
        return "NEWLINE"
    elif char == ',':
        return "COMMA"
    elif char.isspace():
        return "WHITESPACE"
    
    return False

def match_keyword(buffer):
    if buffer in KEYWORDS:
        return f"< KEYWORD , {buffer} >"
    return None

def match_instrument(buffer):
    if buffer in INSTRUMENTS:
        return f"< INSTRUMENT , {buffer} >"
    return None

def match_identifier(buffer):
    if buffer.isalnum() and not buffer[0].isdigit():
        return f"< IDENTIFIER , {buffer} >"
    return None

def match_number(buffer):
    if buffer.isdigit():
        return f"< NUMBER , {buffer} >"
    return None
#############################

def write_output_to_file(output):
    with open("output.txt", "w") as output_file:
        for token in output:
            output_file.write(token + "\n")
    print("Output written to output.txt")

def lexer(input_program):
    try:
        with open(input_program, 'r') as program_body:
            output = []
            buffer = ""
            while True:
                char = program_body.read(1)
                if not char:
                    break  # EOF

                # if delimiter, process buffer and add to output
                delim = match_delimiter(char)
                if delim:
                    if buffer:
                        # we may want to adjust this for matching priority
                        token = (match_keyword(buffer) or 
                                 match_instrument(buffer) or 
                                 match_identifier(buffer) or 
                                 match_number(buffer))
                        if token:
                            output.append(token)
                        # have error token with buffer when error was found,
                        # this way buffer can be handled when doing error processing
                        else:
                            handle_error(buffer)
                            output.append(f"< ERROR , Unrecognized token '{buffer}' >")
                        buffer = ""
                    # whitespace could be potentially ignored, but for now will be recognized as token
                    if delim != "WHITESPACE":
                        output.append(f"< {delim} >")
                    continue

                buffer += char

            # if leftover chars in buffer,
            # process and add to output - cannot have random non-tokens in output
            if buffer:
                token = (match_keyword(buffer) or 
                         match_instrument(buffer) or 
                         match_identifier(buffer) or 
                         match_number(buffer))
                if token:
                    output.append(token)
                else:
                    handle_error(buffer)
                    output.append(f"< ERROR , Unrecognized token '{buffer}' >")

        write_output_to_file(output)

    except FileNotFoundError:
        print(f"Error: The program '{input_program}' was not found.")
    except Exception as e:
        print(f"Error reading file: {e}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python lexer.py <filename>")
    else:
        filename = sys.argv[1]
        lexer(filename)