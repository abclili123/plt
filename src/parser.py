class Node:
    def __init__(self, type, value=None):
        self.type = type
        self.value = value
        self.children = []
    def add_child(self, node):
        if node:
            self.children.append(node)
    def remove_child(self):
            self.children.pop()
    def __str__(self):
        return f"{self.type} ({self.value})"

class Parser:
    def __init__(self, tokens, output_file):
        self.tokens = tokens
        self.index = 0
        self.current_token = self.tokens[self.index] if self.tokens else None
        self.last_token = None
        self.comma_tracker = True

        # verify identifiers
        self.group_identifiers = [] # these are names of groups
        self.loop_or_segment_identifiers = [] # these are the names of loops and segments
        self.play_identifiers = [] # these are idenfiers that follow play statements
        self.identifiers_in_groups = [] # these are identifiers within group statements

        # AST set up
        self.root_node = None
        self.current_node = None
        self.stack = []
        self.output_file = output_file
        self.error = None
        self.errors = []

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
    
    def verify_identifiers():
        # traverse the tree

        # if you are at a group node, verify all identifiers in the body are in self.loop_or_segment_identifiers

        # if you are in a play node
            # if the play node has a body node as a child pass becuase it is defined and played at the same time
            # else verify all identifiers in the play node are in self.identifiers_in_groups or self.loop_or_segment_identifiers
        pass
    
    def print_ast_tree(self, node=None, level=0, prefix=""):
        output_string = ""

        if self.error:
            output_string += self.error
        else:
            if node is None:
                node = self.root_node
                print(f"{node}")
                output_string += f"{node}\n"
            else:
                print(f"{prefix}|-- {node}")
                output_string += f"{prefix}|-- {node}\n"

            for child in node.children:
                new_prefix = prefix + "|   "
                output_string += self.print_ast_tree(child, level + 1, new_prefix)

        # write to output after recursion
        if level == 0:
            with open(self.output_file, "w") as out:
                out.write(output_string)

        return output_string
        
    def consume(self, token_type, token_value=None):
        # consume the current token if it matches, and advance
        if self.match(token_type, token_value):
            token = self.current_token
            print(f"parsing: {token}")
            print(f"last tok: {self.last_token}")
            print(f"current_node: {self.current_node}")
            print("stack before")
            for node in self.stack:
                print(node.type)

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

                if self.last_token[0] == 'IDENTIFIER' and self.comma_tracker == False:
                    self.comma_tracker = True # reset comma tracker
                    self.stack.pop()
                    self.current_node = self.stack[-1] if self.stack else None # set current node to body

                self.current_node.add_child(identifier_node)

                # if current node is a group
                if self.current_node.type == "Group":
                    self.group_identifiers.append(identifier_node)

                # if current node is define
                elif self.current_node.type == "Define":
                    self.loop_or_segment_identifiers.append(identifier_node)

                # if current node is play
                elif self.current_node.type == "Play" or self.stack[-2].type == "Play":
                    self.play_identifiers.append(identifier_node)

                elif self.stack[-2].type == "Group":
                    self.identifiers_in_groups.append(identifier_node)

            elif token_type == "TIME_LITERAL":
                if isinstance(self.current_node, Node) and self.current_node.type == "Tempo":
                    self.current_node.value = token[1]
                else:
                    self.duration_value = token[1]
            elif token_type == "TYPE_TIME":
                duration_node = Node("Duration", f"{self.duration_value} {token[1]}")
                if self.current_node.type == "Sound" and self.stack[-1].type == "Concurrent":
                    self.stack[-1].add_child(duration_node)
                    self.stack.pop()
                    self.current_node = self.stack[-1] if self.stack else None
                    self.comma_tracker = True

                elif self.current_node.type == "Sound" or self.current_node.type == "Rest":
                    self.current_node.add_child(duration_node)
                    self.current_node = self.stack[-1] if self.stack else None
                    self.comma_tracker = True
                
                elif self.current_node.type == "Generate":
                    self.current_node.add_child(duration_node)
                    self.stack.pop()
                    self.current_node = self.stack[-1] if self.stack else None

                else:
                    self.current_node.add_child(duration_node)

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
                # if the current node is concurrent add this node as a child
                sound_node = Node("Sound", token[1])
                self.current_node.add_child(sound_node)

                if self.last_token[0] == 'DESCRIPTION_LITERAL':
                    print("fixing curr node")
                    self.current_node = self.stack[-1]
                else: 
                    self.current_node = sound_node
                # self.stack.append(sound_node)

            elif token_type == "NOTE_LITERAL" or token_type == "CHORD_LITERAL":
                value_node = Node("Value", token[1])
                self.current_node.add_child(value_node)

            elif token_type == "DESCRIPTION_LITERAL":
                desc_node = Node("Description", token[1])
                self.current_node.add_child(desc_node)
            elif token_type == "COMMA":
                if self.comma_tracker:
                    self.comma_tracker = False
                    # if this is the first comma, make a node called concurrent
                    concurrent_node = Node("Concurrent")
                    if self.last_token[0] == 'IDENTIFIER': # in a group node
                        # the current node is body
                        # move the last child into the concurrent node
                        concurrent_node.add_child(self.current_node.children[-1])
                        self.current_node.remove_child()

                    else:
                        # add the current node as a child of concurrent
                        concurrent_node.add_child(self.current_node)
                        # replace the current node with concurrent
                        # first remove sound as a child of body
                        self.stack[-1].remove_child()

                    # then add the current node as a child of body
                    self.stack[-1].add_child(concurrent_node)

                    # then make concurrent node the current node
                    self.current_node = concurrent_node

                    # add it to the stack
                    self.stack.append(self.current_node)
                elif self.last_token[0] == 'NOTE_LITERAL':
                    self.current_node = self.stack[-1]
                    
            elif token_type == "OPENBRACK":
                body_node = Node("Body")
                self.current_node.add_child(body_node)
                self.current_node = body_node
                self.stack.append(body_node)
            elif token_type == "CLOSEBRACK":
                self.stack.pop()
                self.current_node = self.stack[-1] if self.stack else None

            self.last_token = token

            print("tree")
            self.print_ast_tree()
            print(self.comma_tracker)
            print()
            print(f"current_node: {self.current_node}")
            print("stack after")
            for node in self.stack:
                print(node.type)
            print()
            print("___________________________________")
            self.advance()
        else:
            self.error = f"Expected {token_type} ({token_value}), but found {self.current_token}"
            self.errors.append(self.error)

    def parse_program(self):
        # parse the program non-terminal
        if self.match("KEYWORD", "tempo"):
            self.parse_tempo()
            self.parse_statement()
        else:
            self.error = f"Expected 'tempo', but found {self.current_token}"
            self.errors.append(self.error)
            #self.print_ast_tree()
            #raise SyntaxError(f"Expected 'tempo', but found {self.current_token}")

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
            self.error = f"Unexpected token in statement: {self.current_token}"
            self.errors.append(self.error)
            #self.print_ast_tree()
            #raise SyntaxError(f"Unexpected token in statement: {self.current_token}")

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
            self.error = f"Expected 'loop' or 'segment', but found {self.current_token}"
            self.errors.append(self.error)
            #self.print_ast_tree()
            #raise SyntaxError(f"Expected 'loop' or 'segment', but found {self.current_token}")

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
        if self.match("TYPE_SOUND"):
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
            self.error = f"Expected 'note' or 'chord', but found {self.current_token}"
            self.errors.append(self.error)
            #self.print_ast_tree()
            #raise SyntaxError(f"Expected 'note' or 'chord', but found {self.current_token}")

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
            self.error = f"Expected 'note' or 'chord', but found {self.current_token}"
            self.errors.append(self.error)
            #self.print_ast_tree()
            #raise SyntaxError(f"Expected 'note' or 'chord', but found {self.current_token}")

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
            self.error = f"Unexpected token in play_statement: {self.current_token}"
            self.errors.append(self.error)
            #self.print_ast_tree()
            #raise SyntaxError(f"Unexpected token in play_statement: {self.current_token}")

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
