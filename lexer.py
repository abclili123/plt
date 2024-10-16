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
    # if it is one char then it is just a note wihtout an accidental and assumed 4th octave
    if len(buffer) == 1:
        note = buffer[0]
        if note in "ABCDEFGabcdefg":
            return f"< NOTE_LITERAL , {buffer} >"
    
    # if it is two char it can be a note followed be an accidental or an octave
    elif len(buffer) == 2: # a4, a#
        note = buffer[0] in "ABCDEFGabcdefg"
        accidental = buffer[1] in ['#', 'b']
        octave = buffer[1].isdigit()
        if note and (accidental or octave):
            return f"< NOTE_LITERAL , {buffer} >"
    
    # if it is 3 char it can be a note followed be an accidental and an octave
    elif len(buffer) == 3:
        note = buffer[0] in "ABCDEFGabcdefg"
        accidental = buffer[1] in ['#', 'b']
        octave = buffer[2].isdigit()
        if note and accidental and octave:
            return f"< NOTE_LITERAL , {buffer} >"
        
    return False

def match_chord_literal(buffer):
    # if it is one char then it is just a note wihtout an accidental and assumed 4th octave and major
    if len(buffer) == 1:
        note = buffer[0]
        if note in "ABCDEFGabcdefg":
            return f"< CHORD_LITERAL , {buffer} >"
    
    # if it is two char it can be a note followed be an accidental or an octave or a minor
    elif len(buffer) == 2: # a4, a#
        note = buffer[0] in "ABCDEFGabcdefg"
        accidental = buffer[1] in ['#', 'b']
        octave = buffer[1].isdigit()
        minor = buffer[1] == "m"
        if note and (accidental or octave or minor):
            return f"< CHORD_LITERAL , {buffer} >"
    
    # if it is 3 char it can be a note followed be 2 of the following accidental, octave, minor
    elif len(buffer) == 3:
        note = buffer[0] in "ABCDEFGabcdefg"

        # accidental in 1, octave in 2
        # accidental in 1, minor in 2
        accidental = buffer[1] in ['#', 'b']
        octave = buffer[2].isdigit()
        minor = buffer[2] == "m"
        if note and accidental and (octave or minor):
            return f"< CHORD_LITERAL , {buffer} >"
        
        # octave in 1, minor in 2
        octave = buffer[1].isdigit()
        if note and octave and minor:
            return f"< CHORD_LITERAL , {buffer} >"
        
    return False

def match_time_literal(buffer):
    if buffer.isdigit():
        return f"< TIME_LITERAL , {buffer} >"
    elif '.' in buffer:
        parts = buffer.split('.')
        if len(parts) == 2 and all(part.isdigit() or part == "" for part in parts):
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

def write_output_to_file(output, filename):
    with open(filename, "w") as output_file:
        for token in output:
            output_file.write(token + "\n")
    print(f"Output written to {filename}")

def lexer(input_program, output_file):
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
                        
                        # if result is a part and delim is whitespace
                        # need next token to match an identifier
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

        write_output_to_file(output, output_file)

    except FileNotFoundError:
        print(f"Error: The program '{input_program}' was not found.")
    except Exception as e:
        print(f"Error reading file: {e}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python lexer.py <input_filename> <output_filename>")
    else:
        input_file = sys.argv[1]
        output_file = sys.argv[2]
        print(f"Parsing {input_file}")
        lexer(input_file, output_file)