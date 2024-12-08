from parser import Node

# for these each elem will loop like
# identifier: [
#         { instrument: 'instrument_type', sounds: ['note C', 'chord B'], duration: 1 },
#         { instrument: 'instrument_type', sounds: 'rest', duration: 1 },
#         { instrument: 'instrument_type', sounds: 'note G', duration: 1 },
#         { instrument: 'instrument_type', sounds: 'chord A', duration: 1 }
#     ],
loops = ""
segments = ""

# for these each elem will look like
# identifier: [
#     ['identifier', 'identifier'],
#     'identifier',
#     'identifier'
# ]
groups = ""
plays = ""

# this will look like
# not sure yet
control = ""

def generate_code(root_node):
    # traverse tree
    def _write_node(node):

        for child in node:
            _write_node(child)

    _write_node(root_node)