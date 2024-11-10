import sys

grammar = {
    "program": [["tempo", "< NEWLINE >", "statement", "EOF"]],
    "statement": [["define_part", "statement"], ["group", "statement"], ["play_statement"], []],
    "define_part": [["< KEYWORD , define >", "define_type", "< IDENTIFIER >", "< OPENBRACK >", "part_body", "< CLOSEBRACK >", "statement"]],
    "define_type": [["< TYPE_PART , {loop} >"], ["< TYPE_PART , {segment} >"], ["group_body", "EOF"]],
    "part_body": [["instrument_declaration", "sounds"]],
    "instrument_declaration": [["< TYPE_INSTRUMENT >", "< INSTRUMENT_LITERAL >", "< NEWLINE >"]],
   "note_sequence": [
        ["note_or_chord"],
        ["< NOTE_LITERAL >"], 
        ["< TYPE_SOUND, {note} >", "< NOTE_LITERAL >"],
        ["< TYPE_SOUND, {chord} >", "< CHORD_LITERAL >"]
    ],
    "sounds": [
        ["note_sequence", "duration", "sounds"],
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
        ["< KEYWORD , play >", "< IDENTIFIER >"],
        ["< KEYWORD , play >", "define_type", "< IDENTIFIER >", "< OPENBRACK >", "part_body", "< CLOSEBRACK >"]
    ],
    "group": [
        ["< TYPE_GROUP >", "< IDENTIFIER >", "< OPENBRACK >", "group_body", "< CLOSEBRACK >", "statement"]
    ],
    "group_body": [
        ["group_item", "< NEWLINE >", "group_body"],
        []
    ],
    "group_item": [
        ["< IDENTIFIER >"],
        ["< INSTRUMENT_LITERAL >"]
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
    "statement": {"< KEYWORD , define >", "< KEYWORD , play >", "< TYPE_GROUP >", "", "EOF"},
    "define_part": {"< KEYWORD , define >"},
    "define_type": {"< TYPE_PART , {loop} >", "< TYPE_PART , {segment} >", "< IDENTIFIER >"},
    "part_body": {"< TYPE_INSTRUMENT >"},
    "instrument_declaration": {"< TYPE_INSTRUMENT >"},
    "sounds": {"< TYPE_SOUND, {note} >", "< TYPE_SOUND, {chord} >", "< NOTE_LITERAL >", "< KEYWORD , rest >", "< KEYWORD , generate >", "< IDENTIFIER >"},
    "note_chord": {"< TYPE_SOUND, {note} >", "< TYPE_SOUND, {chord} >"},
    "optional_note_chord": {"< COMMA >", ""},
    "duration": {"< TIME_LITERAL >"},
    "tempo": {"< KEYWORD , tempo >"},
    "play_statement": {"< KEYWORD , play >"},
    "group": {"< TYPE_GROUP >"},
    "optional_identifiers": {"< COMMA >", ""},
    "note_sequence": {"< NOTE_LITERAL >", "< TYPE_SOUND, {note} >", "< TYPE_SOUND, {chord} >"},
    "group_body": {"< IDENTIFIER >", "< INSTRUMENT_LITERAL >", ""},
    "group_item": {"< IDENTIFIER >", "< INSTRUMENT_LITERAL >"}
}

# follow sets
# need to fill out
# initialize follow sets with empty sets
follow_sets = {
    "program": set(),
    "statement": set(),
    "define_part": set(),
    "define_type": set(),
    "part_body": set(), 
    "instrument_declaration": set(),
    "sounds": set(),
    "note_or_chord": set(), 
    "note_chord": set(), 
    "optional_note_chord": set(),  
    "duration": set(),  
    "tempo": set(),  
    "play_statement": set(), 
    "group": set(), 
    "optional_identifiers": set() 
}

# then fill the follow sets
follow_sets["program"] = {"EOF"}
follow_sets["statement"] = {"EOF", "< CLOSEBRACK >"}
follow_sets["define_type"] = {"< IDENTIFIER >",}
follow_sets["part_body"] = {"< CLOSEBRACK >"}
follow_sets["instrument_declaration"] = first_sets["sounds"]
follow_sets["sounds"] = {"< CLOSEBRACK >"}
follow_sets["note_or_chord"] = {"< COMMA >", "< TIME_LITERAL >"}
follow_sets["note_chord"] = {"< COMMA >", "< TIME_LITERAL >"}
follow_sets["optional_note_chord"] = {"< TIME_LITERAL >"}
follow_sets["duration"] = first_sets["sounds"].union({"< CLOSEBRACK >"})
follow_sets["tempo"] = {"< NEWLINE >"}
follow_sets["optional_identifiers"] = {"< NEWLINE >"}

follow_sets["define_part"] = first_sets["statement"].union(follow_sets["statement"])
follow_sets["play_statement"] = first_sets["statement"].union(follow_sets["statement"])
follow_sets["group"] = first_sets["statement"].union(follow_sets["statement"])

follow_sets["statement"] = follow_sets["statement"].union(first_sets["statement"])
follow_sets["sounds"] = follow_sets["sounds"].union(first_sets["sounds"])
follow_sets["optional_note_chord"] = follow_sets["optional_note_chord"].union(first_sets["optional_note_chord"])
follow_sets["optional_identifiers"] = follow_sets["optional_identifiers"].union(first_sets["optional_identifiers"])

# error recovery
error_types = ["Syntax Error", "Semantic Error", "Lexical Error", "Type Error"]

grammar["note_or_chord"] = grammar["note_chord"]
first_sets["note_or_chord"] = first_sets["note_chord"]
follow_sets["note_or_chord"] = follow_sets["note_chord"]
first_sets["note_sequence"] = {"< NOTE_LITERAL >", "< TYPE_SOUND, {note} >", "< TYPE_SOUND, {chord} >"}
follow_sets["note_sequence"] = {"< TIME_LITERAL >"}
follow_sets["optional_note_chord"] = {"< TIME_LITERAL >"}
follow_sets["group_body"] = {"< CLOSEBRACK >"}
follow_sets["group_item"] = {"< NEWLINE >"}

# construct parse table
def create_parse_table(grammar, first_sets, follow_sets):
    parse_table = {}
    
    for non_terminal in grammar:
        parse_table[non_terminal] = {}
        
        for production in grammar[non_terminal]:
            if not production: 
                for terminal in follow_sets[non_terminal]:
                    term_type = f"< {terminal.strip('<>').split(',')[0].strip()} >" if terminal.startswith("<") else terminal
                    if term_type not in parse_table[non_terminal]:
                        parse_table[non_terminal][term_type] = production
                continue
                
            first_symbol = production[0]
            
            if first_symbol.startswith("<"):
                if "KEYWORD , play" in first_symbol:
                    # special case for play keyword
                    if non_terminal == "statement":
                        parse_table[non_terminal]["< KEYWORD , play >"] = ["play_statement"]
                    else:
                        parse_table[non_terminal]["< KEYWORD , play >"] = production
                else:
                    term_type = f"< {first_symbol.strip('<>').split(',')[0].strip()} >"
                    if term_type not in parse_table[non_terminal]:
                        parse_table[non_terminal][term_type] = production
            else:
                if first_symbol in first_sets:
                    print(f"    Adding entries from first set of {first_symbol}: {first_sets[first_symbol]}")
                    # add entries for each terminal in the first set of the non-terminal
                    for terminal in first_sets[first_symbol]:
                        if terminal == "":
                            continue
                        if terminal == "EOF":
                            term_type = terminal
                        else:
                            term_type = f"< {terminal.strip('<>').split(',')[0].strip()} >"
                        if term_type not in parse_table[non_terminal]:
                            parse_table[non_terminal][term_type] = production
                else:
                    print(f"Warning: No first set entry for {first_symbol}")
    
    # Debug output
    print("\nParse table entries for sounds:")
    if "sounds" in parse_table:
        for key, value in parse_table["sounds"].items():
            print(f"  {key}: {value}")
    
    return parse_table

def print_ast_tree(node, spacing=0):
    result = " " * spacing + f"{node.type}\n"

    for t, child in node.children:
        if t == "terminal":
            result += " " * (spacing + 2) + f"token: {child}\n"
        else:
            result += print_ast_tree(child, spacing + 2)
    
    return result

# i think we can remove this code to a different file
# and paste the table here so that we're not regenerating the table every time


def parser(input_program, output_file):
    tokens = []
    with open(input_program, 'r') as token_stream:
        for line in token_stream:
            if line.strip(): 
                tokens.append(line.strip())
    
    print("Tokens to parse:", tokens)
    
    parse_tree = ParseTree(tokens)
    ast = parse_tree.parse()
    
    if ast is None:
        print("Failed to generate AST. Errors:")
        for error in parse_tree.errors:
            print(error)
        return
    
    with open(output_file, 'w') as output:
        output.write(print_ast_tree(ast))
    
    if parse_tree.errors:
        print("\nParser errors:")
        for error in parse_tree.errors:
            print(error)      

class TreeNode:
    def __init__(self, type):
        self.type = type
        self.children = []

    def append(self, child_tuple):
        self.children.append(child_tuple)

parse_table = create_parse_table(grammar, first_sets, follow_sets)

class ParseTree:
    def __init__(self, tokens):
        self.tokens = tokens
        self.cursor = 0
        self.grammar = grammar
        self.first_sets = first_sets
        self.follow_sets = follow_sets
        self.parse_table = parse_table
        self.errors = []

    # returns the next token but does not increment the cursor
    def peek(self):
        if self.cursor < len(self.tokens):
            return self.tokens[self.cursor].strip()
        return "EOF"

    # returns the next token and increments the cursor
    def consume(self):
        token = self.peek()
        self.cursor += 1
        return token
    
    def get_token_type(self, token):
        if token == "EOF":
            return token
        if not token.startswith("<"):
            return token
        return token.strip('<>').split(',')[0].strip()

    def match(self, expected):
        token = self.peek()

        expected_type = f"< {self.get_token_type(expected)} >" if expected.startswith("<") else expected
        token_type = f"< {self.get_token_type(token)} >" if token.startswith("<") else token

        print(f"DEBUG: Matching - Expected type: {expected_type}, Token type: {token_type}")

        if expected_type == token_type:
            consumed = self.consume()
            print(f"Matched token: {consumed}")
            return consumed
        # elif (expected_type == "< NEWLINE >" and token == "EOF"):
        #     print("Matched EOF")
        #     return "EOF"

        self.errors.append(f"{error_types[0]} - expected {expected} but got {token} at position {self.cursor}")
        return None

    def should_skip_newlines(self, non_terminal):
        # list of non-terminals where we should skip newlines
        skip_newlines_for = {
            "statement", 
            "sounds", 
            "part_body", 
            "instrument_declaration",
            "group_body"
        }
        return non_terminal in skip_newlines_for

    def skip_newlines(self):
        while self.peek().startswith("< NEWLINE >"):
            self.consume()
            print("Skipping newline")

    def parse_non_terminal(self, non_terminal):
        if self.should_skip_newlines(non_terminal):
            self.skip_newlines()

        curr = self.peek()
        curr_type = f"< {self.get_token_type(curr)} >" if curr.startswith("<") else curr
        print(f"DEBUG: Parsing {non_terminal} with token {curr}")
        print(f"DEBUG: Token type: {curr_type}")
        print(f"DEBUG: Available productions for {non_terminal}: {self.parse_table.get(non_terminal, {})}")

        if non_terminal not in self.parse_table or curr_type not in self.parse_table[non_terminal]:
            available = self.parse_table.get(non_terminal, {}).keys()
            self.errors.append(f"{error_types[0]} - no production for {non_terminal} with token {curr}")
            self.errors.append(f"Available productions were for tokens: {available}")
            return None

        production = self.parse_table[non_terminal][curr_type]
        node = TreeNode(non_terminal)

        for symbol in production:
            if (len(self.tokens) <= self.cursor):
                print("EOF")
                break;
            if symbol == "< NEWLINE >":
                token = self.match(symbol)
                if token:
                    node.children.append(("terminal", token))
                else:
                    return None
                self.skip_newlines()
            elif symbol.startswith("<"):
                token = self.match(symbol)
                if token:
                    node.children.append(("terminal", token))
                else:
                    return None
            elif symbol in self.grammar:
                child = self.parse_non_terminal(symbol)
                if child:
                    node.children.append(("non-terminal", child))
                else:
                    return None
            elif symbol == "EOF":
                if self.peek() != "EOF":
                    self.errors.append(f"{error_types[0]} - expected EOF but got {self.peek()}")
                    return None

        return node
    
    def parse(self):
        return self.parse_non_terminal("program")


def main():
    if len(sys.argv) != 3:
        print("Usage: python parser.py <input_filename> <output_filename>")
    else:
        input_file = sys.argv[1]
        if (input_file[-4:] != ".out"):
            print("Input file must be a .out file")
            print("Make sure lexer has been run first to generate the .out file")
            return
        output_file = sys.argv[2]
        print(f"Parsing {input_file}")
        parser(input_file, output_file)


if __name__ == "__main__":
    main()