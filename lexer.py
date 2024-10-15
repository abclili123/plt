import sys

######## KEYWORDS ########
KEYWORDS = [
    "define",
    "tempo",
    "play",
    "generate",
    "rest"
]
##########################

### INSTRUMENT LITERALS ##
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

#### TYPES ####
TYPES = {
        "loop": "< TYPE_PART , {loop} >",
        "segment": "< TYPE_PART , {segment} >",
        "group": "< TYPE_GROUP >",
        "instrument": "< TYPE_INSTRUMENT >",
        "chord": "< TYPE_SOUND, {chord} >",
        "note": "< TYPE_SOUND, {note} >",
        "beat": "< TYPE_TIME, {beat} >",
        "beats": "< TYPE_TIME, {beats} >",
    }
#####################

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
        return (f"< KEYWORD , {buffer} >", buffer)
    return False

def match_type(buffer):
    if buffer in TYPES.keys():
        return (TYPES[buffer], buffer)
    return False

def match_instrument(buffer):
    if buffer in INSTRUMENTS:
        return f"< INSTRUMENT_LITERAL , {buffer} >", buffer
    return False

def match_note_literal(buffer):
    # Valid lengths for a note are 1 (e.g., A) or 2-3 (e.g., A4, C#5)
    if len(buffer) < 1 or len(buffer) > 3:
        return False  # Invalid length for a note

    # Extract components
    note = buffer[0]
    accidental = buffer[1] if len(buffer) > 1 and buffer[1] in ['#', 'b'] else ''
    octave = buffer[1] if len(buffer) == 2 and buffer[1].isdigit() else buffer[2] if len(buffer) == 3 else ''

    # Check if the note is valid (A-G or a-g)
    if note in "ABCDEFGabcdefg":
        if octave == '' or (octave.isdigit() and 1 <= int(octave) <= 7):
            return f"< NOTE_LITERAL , {buffer} >"

    return False

def match_chord_literal(buffer):
    # Valid lengths for a chord are 1 (e.g., a), 2 (e.g., a#), 3-5 (e.g., a#m, a#minor)
    if len(buffer) < 1 or len(buffer) > 5:
        return False  # Invalid length for a chord

    note = buffer[0]
    accidental = buffer[1] if len(buffer) > 1 and buffer[1] in ['#', 'b'] else ''
    is_minor = buffer.endswith('m') or buffer.endswith('minor')

    # Check if the note is valid (A-G or a-g)
    if note in "ABCDEFGabcdefg":
        # If minor designation is present
        if is_minor:
            if accidental and len(buffer) == 3:  # Valid case like "a#m"
                return f"< CHORD_LITERAL , {buffer} >"
            elif buffer == note + 'minor' and len(buffer) == 6:  # Valid case like "aminor"
                return f"< CHORD_LITERAL , {buffer} >"
            elif accidental == '' and len(buffer) == 2:  # Valid case like "am"
                return f"< CHORD_LITERAL , {buffer} >"
        
        # Determine the octave if it exists
        octave = buffer[2] if len(buffer) == 3 and buffer[2].isdigit() else ''
        if octave == '' and len(buffer) > 2 and accidental and len(buffer) == 4:
            octave = buffer[3]  # e.g., "C#3"

        # Validate octave if present
        if octave == '' or (octave.isdigit() and 1 <= int(octave) <= 7):
            # Form the chord literal without "minor"
            return f"< CHORD_LITERAL , {buffer} >"

    return False

def match_time_literal(buffer):
    if buffer.isdigit():
        return f"< TIME_LITERAL , {buffer} >"
    elif '.' in buffer:
        parts = buffer.split('.')
        if len(parts) == 2 and all(part.isdigit() for part in parts):
            return f"< TIME_LITERAL , {buffer} >"
    return False

def match_description_literal(buffer):
    if buffer.isalpha() and len(buffer) > 0:
        return f"< DESCRIPTION_LITERAL , {buffer} >"
    return False

def match_identifier(buffer):
    if buffer and buffer[0].isalpha() and all(c.isalnum() or c == '_' for c in buffer):
        return f"< IDENTIFIER , {buffer} >"
    return False

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
                        # first match keyword type and instrument
                        token = (match_keyword(buffer) or 
                                         match_type(buffer) or 
                                         match_instrument(buffer)
                                         )
                        result = ""
                        if type(token) == tuple:
                            token, result = token

                        # if result is generate and delim is whitespace
                        # need next token to match a decription literal
                        if result == "generate" and delim == "WHITESPACE":
                            output.append(token)
                            buffer = ""
                            # forward buffer to the next delimiter
                            char = program_body.read(1)
                            buffer += char
                            delim = match_delimiter(char)
                            while not delim:
                                char = program_body.read(1)
                                if not char:  # EOF
                                    break
                                delim = match_delimiter(char)
                                if not delim:
                                    buffer += char

                            if buffer:
                                # match buffer against decription literal
                                token = match_description_literal(buffer)
                        
                        if result == "loop" or result =="segement" and delim == "WHITESPACE":
                            output.append(token)
                            buffer = ""
                            # forward buffer to the next delimiter
                            char = program_body.read(1)
                            buffer += char
                            delim = match_delimiter(char)
                            while not delim:
                                char = program_body.read(1)
                                if not char:  # EOF
                                    break
                                delim = match_delimiter(char)
                                if not delim:
                                    buffer += char

                            if buffer:
                                # match buffer against identifier
                                token = match_identifier(buffer)

                        # if the result is note and delim is whitespace
                        # need the next token to match a note literal
                        elif result == "note" and delim == "WHITESPACE":
                            output.append(token)
                            buffer = ""
                            # forward buffer to the next delimiter
                            char = program_body.read(1)
                            buffer += char
                            delim = match_delimiter(char)
                            while not delim:
                                char = program_body.read(1)
                                if not char:  # EOF
                                    break
                                delim = match_delimiter(char)
                                if not delim:
                                    buffer += char

                            if buffer:
                                # match buffer against note literal
                                token = match_note_literal(buffer)

                        # if the result is chord and delim is whitespace
                        # need the next token to match a note literal
                        elif result == "chord" and delim == "WHITESPACE":
                            output.append(token)
                            buffer = ""
                            # forward buffer to the next delimiter
                            char = program_body.read(1)
                            buffer += char
                            delim = match_delimiter(char)
                            while not delim:
                                char = program_body.read(1)
                                if not char:  # EOF
                                    break
                                delim = match_delimiter(char)
                                if not delim:
                                    buffer += char

                            if buffer:
                                # match buffer against chord_literal
                                token = match_chord_literal(buffer)

                        # match tokens as normal
                        if not token:
                            token = (match_note_literal(buffer) or
                                    match_chord_literal(buffer) or
                                    match_time_literal(buffer) or
                                    match_identifier(buffer) or
                                    match_description_literal(buffer))

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
                         match_type(buffer) or
                         match_instrument(buffer) or
                         match_note_literal(buffer) or
                         match_chord_literal(buffer) or
                         match_time_literal(buffer) or
                         match_identifier(buffer) or
                         match_description_literal(buffer)
                         )
                if type(token) == tuple:
                    token = token[0]

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