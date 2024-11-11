class Node:
    def __init__(self, type, value=None):
        self.type = type
        self.value = value
        self.children = []
    def add_child(self, node):
        if node:
            self.children.append(node)
    def __str__(self):
        return f"{self.type} ({self.value})"



class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.index = 0
        self.current_token = self.tokens[self.index] if self.tokens else None

        # AST set up
        self.root_node = None
        self.current_node = None
        self.stack = []

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
    
    def print_ast_tree(self, node=None, level=0, prefix=""):
        if node is None:
            node = self.root_node
            print(f"{node}")
        else:
            print(f"{prefix}|-- {node}")
            # can change this to space if the |- looks strange

        for child in node.children:
            new_prefix = prefix + "|   "
            self.print_ast_tree(child, level + 1, new_prefix)

    def consume(self, token_type, token_value=None):
        # consume the current token if it matches, and advance
        if self.match(token_type, token_value):
            token = self.current_token
            # if token_type == tempo, define, play, group
            # it becomes the current node
            # expect tempo to be root node
            if token_type == "KEYWORD":
                if token_value == "tempo":
                    self.root_node = Node("Program")
                    tempo_node = Node("Tempo")
                    self.root_node.add_child(tempo_node)
                    self.current_node = tempo_node
                    self.stack.append(tempo_node)
                elif token_value == "define":
                    define_node = Node("Define")
                    self.root_node.add_child(define_node)
                    self.current_node = define_node
                    self.stack.append(define_node)
                elif token_value == "play":
                    play_node = Node("Play")
                    self.root_node.add_child(play_node)
                    self.current_node = play_node
                    self.stack.append(play_node)
                elif token_value == "generate":
                    generate_node = Node("Generate")
                    self.current_node.add_child(generate_node)
                    self.current_node = generate_node
                    self.stack.append(generate_node)
                elif token_value == "rest":
                    rest_node = Node("Rest")
                    self.current_node.add_child(rest_node)
                    self.current_node = rest_node
                    self.stack.append(rest_node)
            elif token_type == "TYPE_GROUP":
                group_node = Node("Group")
                self.root_node.add_child(group_node)
                self.current_node = group_node
                self.stack.append(group_node)
            elif token_type == "IDENTIFIER":
                identifier_node = Node("Identifier", token[1])
                self.current_node.add_child(identifier_node)
            elif token_type == "TIME_LITERAL":
                if isinstance(self.current_node, Node) and self.current_node.type == "Tempo":
                    self.current_node.value = token[1]
                else:
                    self.duration_value = token[1]
            elif token_type == "TYPE_TIME":
                duration_node = Node("Duration", f"{self.duration_value} {token[1]}")
                self.current_node.add_child(duration_node)
                if self.current_node.type == "Sound" or self.current_node.type == "Generate" or self.current_node.type == "Rest":
                    self.stack.pop()
                    self.current_node = self.stack[-1] if self.stack else None
            elif token_type == "TYPE_PART":
                type_node = Node("Type", token[1])
                self.current_node.add_child(type_node)
            elif token_type == "TYPE_INSTRUMENT":
                instrument_node = Node("Instrument")
                self.current_node.add_child(instrument_node)
                self.current_node = instrument_node
                self.stack.append(instrument_node)
            elif token_type == "INSTRUMENT_LITERAL":
                self.current_node.value = token[1]
                self.stack.pop()
                self.current_node = self.stack[-1] if self.stack else None
            elif token_type == "TYPE_SOUND":
                sound_node = Node("Sound", token[1])
                self.current_node.add_child(sound_node)
                self.current_node = sound_node
                self.stack.append(sound_node)
            elif token_type == "NOTE_LITERAL" or token_type == "CHORD_LITERAL":
                value_node = Node("Value", token[1])
                self.current_node.add_child(value_node)
            elif token_type == "DESCRIPTION_LITERAL":
                desc_node = Node("Description", token[1])
                self.current_node.add_child(desc_node)
            elif token_type == "OPENBRACK":
                body_node = Node("Body")
                self.current_node.add_child(body_node)
                self.current_node = body_node
                self.stack.append(body_node)
            elif token_type == "CLOSEBRACK":
                self.stack.pop()
                self.current_node = self.stack[-1] if self.stack else None
            
        
            # else the token and it's value becomes the child of the current node    

            # if the current node changes
            # print the current branch to the AST
            # reset the children 
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
