import random
import json

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
            
        return self._write_code()

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

    def _write_code(self):

        set_up = f""" 
const loops = {json.dumps(self.loops | self.segments, indent=2)};
const groups = {json.dumps(self.groups, indent=2)};
            """
        
        control = ""
        for loop in self.play_sequence:
            if loop in self.loops:
                control += f"""
const {loop}Duration = calculateLoopDuration('{loop}', tempo);\n
playLoop('{loop}', tempo);\n

loopIntervals.push(setInterval(() => {{
    playLoop('{loop}', tempo);
}}, {loop}Duration * 1000));\n\n
                """
            
            elif loop in self.segments:
                control+= f"playLoop('{loop}', tempo);\n"

            elif loop in self.groups:
                control += f"""
const {loop}Duration = calculateGroupDuration('{loop}', tempo);\n
playGroup('{loop}', tempo);\n

loopIntervals.push(setInterval(() => {{
    playGroup('{loop}', tempo);
}}, {loop}Duration * 1000));\n\n
                """

        code_output = f"""
let loopIntervals = [];
var audioCtx;
var globalAnalyser;
var globalGain;
let noteFrequencies;
let chordFrequencies;

{set_up}

const instruments = {{
    bass: (frequency, duration, time) => {{
        const oscillator = audioCtx.createOscillator();
        oscillator.type = 'sawtooth'; // Bass sound
        oscillator.frequency.setValueAtTime(frequency, time);

        const gainNode = audioCtx.createGain();
        gainNode.gain.setValueAtTime(0.5, time); // Set volume
        gainNode.gain.exponentialRampToValueAtTime(0.001, time + duration);

        oscillator.connect(gainNode);
        gainNode.connect(globalGain);

        oscillator.start(time);
        oscillator.stop(time + duration);
    }},
    hihat: (frequency, duration, time) => {{
        const oscillator = audioCtx.createOscillator();
        oscillator.type = 'triangle'; // Hi-hat sound
        oscillator.frequency.setValueAtTime(frequency, time);

        const gainNode = audioCtx.createGain();
        gainNode.gain.setValueAtTime(0.1, time); // Softer volume for hi-hat
        gainNode.gain.exponentialRampToValueAtTime(0.001, time + duration);

        oscillator.connect(gainNode);
        gainNode.connect(globalGain);

        oscillator.start(time);
        oscillator.stop(time + duration);
    }},
    piano: (frequency, duration, time) => {{
        const oscillator = audioCtx.createOscillator();
        oscillator.type = 'sine'; // Piano sound is typically sine or a combination of sine waves
        oscillator.frequency.setValueAtTime(frequency, time);

        const gainNode = audioCtx.createGain();
        gainNode.gain.setValueAtTime(0.6, time); // A bit louder than hi-hat
        gainNode.gain.exponentialRampToValueAtTime(0.001, time + duration);

        oscillator.connect(gainNode);
        gainNode.connect(globalGain);

        oscillator.start(time);
        oscillator.stop(time + duration);
    }},
    guitar: (frequency, duration, time) => {{
        const oscillator = audioCtx.createOscillator();
        oscillator.type = 'square'; // Guitar sound often has a square or sawtooth wave
        oscillator.frequency.setValueAtTime(frequency, time);

        const gainNode = audioCtx.createGain();
        gainNode.gain.setValueAtTime(0.4, time); // Moderate volume
        gainNode.gain.exponentialRampToValueAtTime(0.001, time + duration);

        oscillator.connect(gainNode);
        gainNode.connect(globalGain);

        oscillator.start(time);
        oscillator.stop(time + duration);
    }},
    horn: (frequency, duration, time) => {{
        const oscillator = audioCtx.createOscillator();
        oscillator.type = 'triangle'; // Horns typically have a smooth but sharp sound
        oscillator.frequency.setValueAtTime(frequency, time);

        const gainNode = audioCtx.createGain();
        gainNode.gain.setValueAtTime(0.8, time); // Louder volume for the horn
        gainNode.gain.exponentialRampToValueAtTime(0.001, time + duration);

        oscillator.connect(gainNode);
        gainNode.connect(globalGain);

        oscillator.start(time);
        oscillator.stop(time + duration);
    }},
    snare: (frequency, duration, time) => {{
        const noiseBuffer = audioCtx.createBuffer(1, audioCtx.sampleRate * duration, audioCtx.sampleRate);
        const noiseData = noiseBuffer.getChannelData(0);
        for (let i = 0; i < noiseData.length; i++) {{
            noiseData[i] = Math.random() * 2 - 1; // White noise
        }}

        const noiseSource = audioCtx.createBufferSource();
        noiseSource.buffer = noiseBuffer;

        const filter = audioCtx.createBiquadFilter();
        filter.type = 'highpass'; // Highpass filter to cut low frequencies
        filter.frequency.setValueAtTime(2000, time); // Snare sound has a high-frequency characteristic

        const gainNode = audioCtx.createGain();
        gainNode.gain.setValueAtTime(0.7, time); // Moderate gain for snare

        noiseSource.connect(filter);
        filter.connect(gainNode);
        gainNode.connect(globalGain);

        noiseSource.start(time);
        noiseSource.stop(time + duration);
    }}
}};


function playGroup(groupName, tempo, startTime = audioCtx.currentTime) {{
    const group = groups[groupName];
    console.log('Playing group:', groupName, 'with structure:', group);

    if (!group) {{
        console.error(`Group "${{groupName}}" is not defined.`);
        return;
    }}

    if (!Array.isArray(group)) {{
        console.error(`Group "${{groupName}}" is not defined as an array.`);
        return;
    }}

    group.forEach(loopName => {{
        if (Array.isArray(loopName)) {{
            // Simultaneous playback
            // Start all simultaneous loops at the same startTime
            let simultaneousStartTime = startTime;
            loopName.forEach(innerLoopName => {{
                if (loops[innerLoopName]) {{
                    playLoop(innerLoopName, tempo, simultaneousStartTime);
                }} else {{
                    console.error(`Loop "${{innerLoopName}}" is not defined.`);
                }}
            }});

            // After all simultaneous loops, calculate the duration of the longest loop
            const totalSimultaneousDuration = Math.max(...loopName.map(innerLoopName => {{
                return calculateLoopDuration(innerLoopName, tempo);
            }}));

            // Update startTime to the end of the longest simultaneous loop
            startTime += totalSimultaneousDuration;
        }} else {{
            // Sequential playback for single loop
            if (loops[loopName]) {{
                playLoop(loopName, tempo, startTime);
                // Update startTime to the end of this loop
                startTime += calculateLoopDuration(loopName, tempo);
            }} else {{
                console.error(`Loop "${{loopName}}" is not defined.`);
            }}
        }}
    }});
}}


function calculateLoopDuration(loopName, tempo) {{
    const beatDuration = 60 / tempo;
    const loop = loops[loopName];
    return loop.reduce((totalDuration, step) => totalDuration + (step.duration || 1) * beatDuration, 0);
}}

function calculateGroupDuration(groupName, tempo) {{
    const group = groups[groupName];
    let totalDuration = 0;

    if (!Array.isArray(group)) {{
        console.error(`Group "${{groupName}}" is not defined as an array.`);
        return 0;
    }}

    // Iterate through each element in the group
    group.forEach(element => {{
        console.log(element)
        if (Array.isArray(element)) {{
            // If the element is an array (simultaneous loops), calculate the duration of each loop
            // and add the largest duration to total
            const maxDuration = Math.max(...element.map(loopName => calculateLoopDuration(loopName, tempo)));
            totalDuration += maxDuration;
        }} else {{
            // If the element is a single loop, just add its duration
            totalDuration += calculateLoopDuration(element, tempo);
        }}
    }});

    return totalDuration;
}}

function playLoop(loopName, tempo, startTime = audioCtx.currentTime) {{
    const loop = loops[loopName];
    const beatDuration = 60 / tempo; // Duration of one beat in seconds

    for (let i = 0; i < loop.length; i++) {{
        let step = loop[i];
        let time = startTime;

        // Check for 'rest'
        if (step.sounds === 'rest') {{
            // Skip playing any sound during a rest, just increment time
            startTime += step.duration * beatDuration;  // Add duration of the rest in seconds
            continue;  // Skip to the next step
        }}

        // Handle other sound types (notes and chords)
        if (Array.isArray(step.sounds)) {{
            // Play simultaneous sounds (notes or chords)
            step.sounds.forEach(sound => {{
                if (sound.startsWith('note')) {{
                    const note = sound.split(' ')[1];
                    const frequency = noteFrequencies[`${{note}}`]; // Default octave is 4
                    if (frequency) {{
                        instruments[step.instrument](frequency, step.duration * beatDuration, time);
                    }} else {{
                        console.error(`Invalid frequency for note: ${{note}}`);
                    }}
                }} else if (sound.startsWith('chord')) {{
                    const chord = sound.split(' ')[1];
                    if (chordFrequencies[chord]) {{
                        chordFrequencies[chord].forEach(frequency => {{
                            instruments[step.instrument](frequency, step.duration * beatDuration, time);
                        }});
                    }} else {{
                        console.error(`Chord "${{chord}}" is not defined.`);
                    }}
                }}
            }});
        }} else {{
            // Play a single note or chord
            if (step.sounds.startsWith('note')) {{
                const note = step.sounds.split(' ')[1];
                const frequency = noteFrequencies[`${{note}}`]; // Default octave is 4
                if (frequency) {{
                    instruments[step.instrument](frequency, step.duration * beatDuration, time);
                }} else {{
                    console.error(`Invalid frequency for note: ${{note}}`);
                }}
            }} else if (step.sounds.startsWith('chord')) {{
                const chord = step.sounds.split(' ')[1];
                if (chordFrequencies[chord]) {{
                    chordFrequencies[chord].forEach(frequency => {{
                        instruments[step.instrument](frequency, step.duration * beatDuration, time);
                    }});
                }} else {{
                    console.error(`Chord "${{chord}}" is not defined.`);
                }}
            }}
        }}

        // Increment startTime for the next step based on the duration of the current step
        startTime += step.duration * beatDuration;
    }}
}}

// def frequencies for notes
function generateFrequencyMap() {{
    // Notes with sharps and flats
    const noteNames = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B'];
    const flatEquivalents = {{
        'C#': 'Db',
        'D#': 'Eb',
        'F#': 'Gb',
        'G#': 'Ab',
        'A#': 'Bb'
    }};

    const frequencyMap = {{}};
    const A4 = 440; // Reference frequency for A4
    const A4Index = noteNames.indexOf('A') + (4 * 12); // Index of A4

    for (let octave = 0; octave <= 7; octave++) {{
        for (let i = 0; i < noteNames.length; i++) {{
            const noteIndex = i + (octave * 12);
            const stepsFromA4 = noteIndex - A4Index;
            const frequency = A4 * Math.pow(2, stepsFromA4 / 12);
            const noteName = `${{noteNames[i]}}${{octave}}`;

            // Add sharp note
            frequencyMap[noteName] = parseFloat(frequency.toFixed(2));

            // Add flat equivalent if it exists
            if (flatEquivalents[noteNames[i]]) {{
                const flatName = `${{flatEquivalents[noteNames[i]]}}${{octave}}`;
                frequencyMap[flatName] = parseFloat(frequency.toFixed(2));
            }}

        }}
    }}

    return frequencyMap;
}}

function generateChordMap() {{
    const chordMap = {{}};

    // Chord intervals for major and minor
    const chordIntervals = {{
        'maj': [0, 4, 7], // Major: Root, Major Third, Perfect Fifth
        'm': [0, 3, 7],   // Minor: Root, Minor Third, Perfect Fifth
    }};

    // Notes with natural, sharp, and flat notes
    const noteNames = ['A', 'A#', 'B', 'C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#'];

    // Iterate over each note from A to G
    noteNames.forEach(rootNote => {{
        // Generate major and minor chords for octaves 1 to 7
        for (let octave = 1; octave <= 7; octave++) {{
            Object.keys(chordIntervals).forEach(chordType => {{
                const intervals = chordIntervals[chordType];
                const chordName = `${{rootNote}}${{octave}}${{chordType === 'maj' ? '' : chordType}}`;

                // Find the root note's frequency
                const rootFrequency = noteFrequencies[rootNote + octave];  // Example: 'A4', 'C5'

                // Create an array to store the frequencies for the chord
                const chordFrequencies = intervals.map(interval => {{
                    const noteIndex = noteNames.indexOf(rootNote) + interval;
                    const wrappedIndex = (noteIndex + 12) % 12;  // Wrap around to avoid negative indexes
                    const noteName = noteNames[wrappedIndex];
                    const frequency = noteFrequencies[noteName + octave];
                    return frequency;
                }});

                // Store the chord frequencies in the chord map
                chordMap[chordName] = chordFrequencies;
            }});
        }}
    }});

    return chordMap;
}}

// audio set up
function initAudio() {{
    // this is so you can hear the audio
    audioCtx = new (window.AudioContext || window.webkitAudioContext)
    globalGain = audioCtx.createGain(); //this will control the volume of all notes
    globalGain.gain.setValueAtTime(0.8, audioCtx.currentTime)
    globalGain.connect(audioCtx.destination);
    globalAnalyser = audioCtx.createAnalyser();
    globalGain.connect(globalAnalyser);
    globalGain.connect(globalAnalyser);
    peak();

    // freq map
    noteFrequencies = generateFrequencyMap();
    chordFrequencies = generateChordMap();
}}

var maxAlltime = 0
function peak() {{
    globalAnalyser.fftSize = 2048;
    var bufferLength = globalAnalyser.frequencyBinCount;
    var dataArray = new Uint8Array(bufferLength);
    globalAnalyser.getByteTimeDomainData(dataArray);

    //values range 0-255, over the range -1,1, so we find the max value from a frame, and then scale
    var maxValue = (dataArray.reduce((max, curr) => (curr > max ? curr : max)) - 128) / 127.0;
    //console.log(maxValue);
    if (maxValue > maxAlltime){{
        maxAlltime = maxValue;
        //console.log("New record! -> " + maxAlltime);
    }}
    requestAnimationFrame(peak);
}}

let loopInterval; // Store the interval ID for stopping

function play() {{
    initAudio();
    
    const tempo = {int(self.tempo)};

    {control}
}}
        """
        
        return code_output

