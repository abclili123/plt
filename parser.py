import sys

grammar = {
    "program": [["tempo", "< NEWLINE >", "statement", "EOF"]],
    "statement": [["define_part"], ["group"], ["play_statement"], []],
    "define_part": [["< KEYWORD , define >", "define_type", "< IDENTIFIER >", "< OPENBRACK >", "part_body", "< CLOSEBRACK >", "statement"]],
    "define_type": [["< TYPE_PART , {loop} >"], ["< TYPE_PART , {segment} >"]],
    "part_body": [["instrument_declaration", "sounds"]],
    "instrument_declaration": [["< TYPE_INSTRUMENT >", "< INSTRUMENT_LITERAL >", "< NEWLINE >"]],
    "sounds": [
        ["note_or_chord", "optional_note_chord", "duration", "sounds"],
        ["< KEYWORD , rest >", "duration", "sounds"],
        ["< KEYWORD , generate >", "< DESCRIPTION_LITERAL >", "< TYPE_SOUND, {note} >", "duration", "sounds"],
        ["< IDENTIFIER >", "< NEWLINE >", "sounds"],
        [],
    ],
    "note_chord": [
        ["< TYPE_SOUND, {note} >", "< NOTE_LITERAL >"],
        ["< TYPE_SOUND, {chord} >", "< CHORD_LITERAL >"]
    ],
    "optional_note_chord": [
        ["< COMMA >", "note_or_chord", "optional_note_chord"],
        []
    ],
    "duration": [["< TIME_LITERAL >", "< TYPE_TIME >", "< NEWLINE >"]],
    "tempo": [["< KEYWORD , tempo >", "< TIME_LITERAL >"]],
    "play_statement": [
        ["< KEYWORD , play >", "< IDENTIFIER >", "statement"],
        ["< KEYWORD , play >", "define_type", "< IDENTIFIER >", "< OPENBRACK >", "part_body", "< CLOSEBRACK >", "statement"]
    ],
    "group": [
        ["< TYPE_GROUP >", "< IDENTIFIER >", "< OPENBRACK >", "< IDENTIFIER >", "optional_identifiers", "< NEWLINE >", "< CLOSEBRACK >", "statement"]
    ],
    "optional_identifiers": [
        ["< COMMA >", "< IDENTIFIER >", "optional_identifiers"],
        []
    ]
}

# first set
# need to double check
first_sets = {
    "program": {"< KEYWORD , tempo >", "EOF"},
    "statement": {"< KEYWORD , define >", "< TYPE_GROUP >", "< KEYWORD , play >", "EOF"},
    "define_part": {"< KEYWORD , define >"},
    "define_type": {"< TYPE_PART , {loop} >", "< TYPE_PART , {segment} >"},
    "part_body": {"< TYPE_INSTRUMENT >"},
    "instrument_declaration": {"< TYPE_INSTRUMENT >"},
    "sounds": {"< TYPE_SOUND, {note} >", "< TYPE_SOUND, {chord} >", "< KEYWORD , rest >", "< KEYWORD , generate >", "< IDENTIFIER >"},
    "note_chord": {"< TYPE_SOUND, {note} >", "< TYPE_SOUND, {chord} >"},
    "optional_note_chord": {"< COMMA >", []},
    "duration": {"< TIME_LITERAL >"},
    "tempo": {"< KEYWORD , tempo >"},
    "play_statement": {"< KEYWORD , play >"},
    "group": {"< TYPE_GROUP >"},
    "optional_identifiers": {"< COMMA >", []}
}

# follow sets
# need to fill out
follow_sets = {
    "program": {},
    "statement": {},
    "define_part": {},
    "define_type": {},
    "part_body": {},
    "instrument_declaration": {},
    "sounds": {},
    "note_chord": {},
    "optional_note_chord": {},
    "duration": {},
    "tempo": {},
    "play_statement": {},
    "group": {},
    "optional_identifiers": {}
}

# construct parse table
def create_parse_table(grammar, first, follow):


    return parse_table

# i think we can remove this code to a different file
# and paste the table here so that we're not regenerating the table every time
parse_table = create_parse_table(grammar, first_sets, follow_sets)


def parser(input_program, output_file):
    with open(input_program, 'r') as token_stream:
        for token in token_stream:
    


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python parser.py <input_filename> <output_filename>")
    else:
        input_file = sys.argv[1]
        output_file = sys.argv[2]
        print(f"Parsing {input_file}")
        parser(input_file, output_file)