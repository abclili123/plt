import random

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

class Generator:
    def __init__(self):
        # init of things that will be used in the code generation
        self.loops = {}
        self.segments = {}
        self.groups = {}
        self.tempo = None
        self.play_sequence = []
        self.current_instrument = None

    def _process_sound(self, node):
        # this is where we actually get the sound value and duration
        # waveform can be generated from the node data
        if node.type == "Concurrent":
            # handle multiple sounds played at once
            sounds = []
            duration = None
            for child in node.children:
                if child.type == "Sound":
                    sound_type = child.value  # note or chord
                    value = next((c.value for c in child.children if c.type == "Value"), None)
                    if value:
                        sounds.append(f"{sound_type} {value}")
                elif child.type == "Duration":
                    duration = float(child.value.split()[0])
            
            return {
                'instrument': self.current_instrument,
                'sounds': sounds,
                'duration': duration
            }
        
        # handle single sounds
        elif node.type == "Sound":
            value = next((c.value for c in node.children if c.type == "Value"), None)
            duration = next((float(c.value.split()[0]) for c in node.children if c.type == "Duration"), None)
            
            return {
                'instrument': self.current_instrument,
                'sounds': f"{node.value} {value}",
                'duration': duration
            }
        
        # handle generate
        elif node.type == "Generate":
            duration = next((float(c.value.split()[0]) for c in node.children if c.type == "Duration"), None)
            sound_type = next((c.value for c in node.children if c.type == "Sound"), None)

            root = random.choice(['A', 'B', 'C', 'D', 'E', 'F', 'G', 'Ab', 'A#', 'Bb', 'B#', 'C#', 'Db', 'D#', 'Eb', 'E#', 'Fb', 'F#', 'Gb', 'G#'])
            octave = random.choice(['1', '2', '3', '4', '5', '6', '7'])

            if sound_type == "note":
                sound = root + octave
            else:
                m = random.choice(['', 'm'])
                sound = root + octave + m

            return {
                'instrument': self.current_instrument,
                'sounds': sound,
                'duration': duration
            }
        
        # handle rests
        elif node.type == "Rest":
            duration = next((float(c.value.split()[0]) for c in node.children if c.type == "Duration"), None)
            return {
                'instrument': self.current_instrument,
                'sounds': "rest",
                'duration': duration
            }

    def _process_define(self, node):
        type_node = next(child for child in node.children if child.type == "Type")
        identifier = next(child for child in node.children if child.type == "Identifier")
        body = next(child for child in node.children if child.type == "Body")
        
        sounds_list = []
        
        # process each sound in the body
        # if the sound is a concurrent sound, process each sound in the concurrent sound
        # sounds declared in the same line are grouped together so duration is constant for both
        for child in body.children:
            if child.type == "Instrument":
                self.current_instrument = child.value
            elif child.type == "Concurrent":
                sounds_list.append(self._process_sound(child))
            elif child.type in ["Sound", "Rest", "Generate"]:
                sounds_list.append(self._process_sound(child))
        
        # put the found value in corresponding dictionary
        if type_node.value == "loop":
            self.loops[identifier.value] = sounds_list
        else:
            self.segments[identifier.value] = sounds_list

    def _process_group(self, node):
        identifier = next(child for child in node.children if child.type == "Identifier")
        body = next(child for child in node.children if child.type == "Body")
        
        group_parts = []
        current_concurrent = [] # bad name lmao
        
        # id groups by identifier, concurrents are in the same list
        for child in body.children:
            if child.type == "Identifier":
                group_parts.append(child.value)
            elif child.type == "Concurrent":
                concurrent_ids = [c.value for c in child.children if c.type == "Identifier"]
                group_parts.append(concurrent_ids)
        
        self.groups[identifier.value] = group_parts

    def _process_play(self, node):        
        for child in node.children:
            if child.type == "Identifier":
                self.play_sequence.append(child.value)
            elif child.type == "Concurrent":
                concurrent_parts = [c.value for c in child.children if c.type == "Identifier"]
                for c in concurrent_parts:
                    self.play_sequence.append(c)
            elif child.type == "Body":
                self._process_define(node)

    def generate_code(self, root_node):
        # tree traversal
        # iterate through the children of the root node
        if root_node.type != "Program":
            raise ValueError("root node was not a Program node")
        
        for child in root_node.children:
            self._process_node(child)
            
        return self._format_output()

    def _process_node(self, node):
        # defines
        if node.type == "Tempo":
            self.tempo = node.value
        
        elif node.type == "Define":
            self._process_define(node)
            
        elif node.type == "Group":
            self._process_group(node)
            
        elif node.type == "Play":
            self._process_play(node)

    def _format_output(self):
        return {
            'tempo': int(self.tempo),
            'loops': self.loops,
            'segments': self.segments,
            'groups': self.groups,
            'play_sequence': self.play_sequence
        }