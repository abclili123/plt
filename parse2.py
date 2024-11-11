class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.index = 0
        self.current_token = self.tokens[self.index] if self.tokens else None

    def advance(self):
        """Move to the next token in the input."""
        self.index += 1
        if self.index < len(self.tokens):
            self.current_token = self.tokens[self.index]
        else:
            self.current_token = None

    def match(self, token_type, token_value=None):
        """Check if the current token matches the expected type (and value, if provided)."""
        if self.current_token is None:
            return False
        
        if self.current_token[0] != token_type:
            return False
        if token_value and self.current_token[1] != token_value:
            return False
        return True

    def consume(self, token_type, token_value=None):
        """Consume the current token if it matches, and advance."""
        if self.match(token_type, token_value):
            self.advance()
        else:
            raise SyntaxError(f"Expected {token_type} ({token_value}), but found {self.current_token}")

    def parse_program(self):
        """Parse the 'program' non-terminal."""
        if self.match("KEYWORD", "tempo"):
            self.parse_tempo()
            self.parse_statement()
        else:
            raise SyntaxError(f"Expected 'tempo', but found {self.current_token}")

    def parse_statement(self):
        """Parse the 'statement' non-terminal."""
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
        """Parse the 'define_part' non-terminal."""
        self.consume("KEYWORD", "define")
        self.parse_define_type()
        self.consume("IDENTIFIER")
        self.consume("OPENBRACK")
        self.parse_part_body()
        self.consume("CLOSEBRACK")
        self.parse_statement()

    def parse_define_type(self):
        """Parse the 'define_type' non-terminal."""
        if self.match("TYPE_PART", "loop"):
            self.consume("TYPE_PART", "loop")
        elif self.match("TYPE_PART", "segment"):
            self.consume("TYPE_PART", "segment")
        else:
            raise SyntaxError(f"Expected 'loop' or 'segment', but found {self.current_token}")

    def parse_part_body(self):
        """Parse the 'part_body' non-terminal."""
        self.parse_instrument_declaration()
        self.parse_sounds()

    def parse_instrument_declaration(self):
        """Parse the 'instrument_declaration' non-terminal."""
        self.consume("TYPE_INSTRUMENT")
        self.consume("INSTRUMENT_LITERAL")

    def parse_sounds(self):
        """Parse the 'sounds' non-terminal."""
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
        """Parse the 'note_or_chord' non-terminal."""
        if self.match("TYPE_SOUND", "note"):
            self.consume("TYPE_SOUND", "note")
            self.consume("NOTE_LITERAL")
        elif self.match("TYPE_SOUND", "chord"):
            self.consume("TYPE_SOUND", "chord")
            self.consume("CHORD_LITERAL")
        else:
            raise SyntaxError(f"Expected 'note' or 'chord', but found {self.current_token}")

    def parse_optional_note_chord(self):
        """Parse the 'optional_note_chord' non-terminal."""
        if self.match("COMMA"):
            self.consume("COMMA")
            self.parse_note_or_chord()
            self.parse_optional_note_chord()
        else:
            return  # epsilon (empty production)

    def parse_generate_sounds(self):
        """Parse the 'generate_sounds' non-terminal."""
        self.consume("DESCRIPTION_LITERAL")
        if self.match("TYPE_SOUND", "note"):
            self.consume("TYPE_SOUND", "note")
        elif self.match("TYPE_SOUND", "chord"):
            self.consume("TYPE_SOUND", "chord")
        else:
            raise SyntaxError(f"Expected 'note' or 'chord', but found {self.current_token}")

    def parse_optional_generate_sounds(self):
        """Parse the 'optional_generate_sounds' non-terminal."""
        if self.match("COMMA"):
            self.consume("COMMA")
            self.parse_generate_sounds()
            self.parse_optional_generate_sounds()
        else:
            return  # epsilon (empty production)

    def parse_duration(self):
        """Parse the 'duration' non-terminal."""
        self.consume("TIME_LITERAL")
        self.consume("TYPE_TIME")

    def parse_tempo(self):
        """Parse the 'tempo' non-terminal."""
        self.consume("KEYWORD", "tempo")
        self.consume("TIME_LITERAL")

    def parse_play_statement(self):
        """Parse the 'play_statement' non-terminal."""
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
        """Parse the 'group' non-terminal."""
        self.consume("TYPE_GROUP")
        self.consume("IDENTIFIER")
        self.consume("OPENBRACK")
        self.parse_group_body()
        self.consume("CLOSEBRACK")
        self.parse_statement()
    
    def parse_group_body(self):
        if self.match("IDENTIFIER"):
            self.consume("IDENTIFIER")
            self.parse_optional_identifiers()
            self.parse_group_body()
        else:
            return  # epsilon (empty production)

    def parse_optional_identifiers(self):
        """Parse the 'optional_identifiers' non-terminal."""
        if self.match("COMMA"):
            self.consume("COMMA")
            self.consume("IDENTIFIER")
            self.parse_optional_identifiers()
        else:
            return  # epsilon (empty production)











