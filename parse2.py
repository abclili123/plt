class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.index = 0
        self.current_token = self.tokens[self.index] if self.tokens else None

        # AST set up
        self.current_node = None
        self.current_children = []

    def advance(self):
        # move to the next token in the input
        self.index += 1
        if self.index < len(self.tokens):
            self.current_token = self.tokens[self.index]
        else:
            self.current_token = None

    def match(self, token_type, token_value=None):
        # check if the current token matches the expected type (and value, if provided)
        if self.current_token is None:
            return False
        
        if self.current_token[0] != token_type:
            return False
        if token_value and self.current_token[1] != token_value:
            return False
        return True

    def consume(self, token_type, token_value=None):
        # consume the current token if it matches, and advance
        if self.match(token_type, token_value):
            # if token_type == tempo, define, play, group
            # it becomes the current node

            # else the token and it's value becomes the child

            # if the current node changes
            # print the current branch to the AST


            self.advance()
        else:
            raise SyntaxError(f"Expected {token_type} ({token_value}), but found {self.current_token}")

    def parse_program(self):
        # parse the program non-terminal
        if self.match("KEYWORD", "tempo"):
            self.parse_tempo()
            self.parse_statement()
        else:
            raise SyntaxError(f"Expected 'tempo', but found {self.current_token}")

    def parse_statement(self):
        # arse the statement non-terminal
        if self.match("KEYWORD", "define"):
            self.parse_define_part()
        elif self.match("TYPE_GROUP"):
            self.parse_group()
        elif self.match("KEYWORD", "play"):
            self.parse_play_statement()
        elif self.current_token == None:
            print("successful parse")
            return  # epsilon (empty production)
        else:
            raise SyntaxError(f"Unexpected token in statement: {self.current_token}")

    def parse_define_part(self):
        # parse the define_part non-terminal
        self.consume("KEYWORD", "define")
        self.parse_define_type()
        self.consume("IDENTIFIER")
        self.consume("OPENBRACK")
        self.parse_part_body()
        self.consume("CLOSEBRACK")
        self.parse_statement()

    def parse_define_type(self):
        # parse the define_type non-terminal
        if self.match("TYPE_PART", "loop"):
            self.consume("TYPE_PART", "loop")
        elif self.match("TYPE_PART", "segment"):
            self.consume("TYPE_PART", "segment")
        else:
            raise SyntaxError(f"Expected 'loop' or 'segment', but found {self.current_token}")

    def parse_part_body(self):
        # parse the part_body non-terminal
        self.parse_instrument_declaration()
        self.parse_sounds()

    def parse_instrument_declaration(self):
        # parse the instrument_declaration non-terminal
        self.consume("TYPE_INSTRUMENT")
        self.consume("INSTRUMENT_LITERAL")

    def parse_sounds(self):
        # parse the sounds non-terminal
        if self.match("TYPE_SOUND", "note"):
            self.parse_note_or_chord()
            self.parse_optional_note_chord()
            self.parse_duration()
            self.parse_sounds()
        elif self.match("KEYWORD", "rest"):
            self.consume("KEYWORD", "rest")
            self.parse_duration()
            self.parse_sounds()
        elif self.match("KEYWORD", "generate"):
            self.consume("KEYWORD", "generate")
            self.parse_generate_sounds()
            self.parse_optional_generate_sounds()
            self.parse_duration()
            self.parse_sounds()
        elif self.match("IDENTIFIER"):
            self.consume("IDENTIFIER")
            self.parse_sounds()
        else:
            return  # epsilon (empty production)

    def parse_note_or_chord(self):
        # parse the note_chord non-terminal
        if self.match("TYPE_SOUND", "note"):
            self.consume("TYPE_SOUND", "note")
            self.consume("NOTE_LITERAL")
        elif self.match("TYPE_SOUND", "chord"):
            self.consume("TYPE_SOUND", "chord")
            self.consume("CHORD_LITERAL")
        else:
            raise SyntaxError(f"Expected 'note' or 'chord', but found {self.current_token}")

    def parse_optional_note_chord(self):
        # parse the the (< COMMA > <note_or_chord>)* for adding a list of notes and chords
        if self.match("COMMA"):
            self.consume("COMMA")
            self.parse_note_or_chord()
            self.parse_optional_note_chord()
        else:
            return  # epsilon (empty production)

    def parse_generate_sounds(self):
        # parse the generating from sounds
        self.consume("DESCRIPTION_LITERAL")
        if self.match("TYPE_SOUND", "note"):
            self.consume("TYPE_SOUND", "note")
        elif self.match("TYPE_SOUND", "chord"):
            self.consume("TYPE_SOUND", "chord")
        else:
            raise SyntaxError(f"Expected 'note' or 'chord', but found {self.current_token}")

    def parse_optional_generate_sounds(self):
        # parse the generating more than one sound
        if self.match("COMMA"):
            self.consume("COMMA")
            self.parse_generate_sounds()
            self.parse_optional_generate_sounds()
        else:
            return  # epsilon (empty production)

    def parse_duration(self):
        # parse the duration non-terminal
        self.consume("TIME_LITERAL")
        self.consume("TYPE_TIME")

    def parse_tempo(self):
        # parse the tempo non-terminal
        self.consume("KEYWORD", "tempo")
        self.consume("TIME_LITERAL")

    def parse_play_statement(self):
        # parse the play_statement non-terminal
        self.consume("KEYWORD", "play")
        if self.match("IDENTIFIER"):
            self.consume("IDENTIFIER")
            self.parse_optional_identifiers()
            self.parse_statement()
        elif self.match("TYPE_PART"):
            self.parse_define_type()
            self.consume("IDENTIFIER")
            self.consume("OPENBRACK")
            self.parse_part_body()
            self.consume("CLOSEBRACK")
            self.parse_statement()
        else:
            raise SyntaxError(f"Unexpected token in play_statement: {self.current_token}")

    def parse_group(self):
        # parse the group non-terminal
        self.consume("TYPE_GROUP")
        self.consume("IDENTIFIER")
        self.consume("OPENBRACK")
        self.parse_group_body()
        self.consume("CLOSEBRACK")
        self.parse_statement()
    
    def parse_group_body(self):
        # parse the group's body
        if self.match("IDENTIFIER"):
            self.consume("IDENTIFIER")
            self.parse_optional_identifiers()
            self.parse_group_body()
        else:
            return  # epsilon (empty production)

    def parse_optional_identifiers(self):
        # parse the (< IDENTIFIER > (< COMMA > < IDENTIFIER >)* for grouping multiple parts
        if self.match("COMMA"):
            self.consume("COMMA")
            self.consume("IDENTIFIER")
            self.parse_optional_identifiers()
        else:
            return  # epsilon (empty production)
