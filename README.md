# plt project

Language summary:

Lexical Grammar:
Keywords:
KEYWORD = define | tempo | play | generate | rest
define: This keyword is used to define a part of the program, being a loop or segment
tempo: This keyword is used to set the pace of the music
play: This keyword is used to start playing a loop, segment, or group
generate: This keyword is used to declare an AI generated chord. It is followed by a DESCRIPTION_LITERAL used to generate the chord

Types:
TYPE_PART = loop | segment
loop and segment define parts of the program. loops are sequences of notes and chords that repeat. segments are the same but do not repeat.
TYPE_GROUP = group
group is used to chain parts (loops and segments) together so that they can be played easier
TYPE_INSTRUMENT = instrument
instrument is a reserved type used to denote that the next token is the instrument to be played in that part
TYPE_SOUND = chord | note
chord and note are types of sounds that instruments can play
TYPE_TIME = beat 
beat describes the number as a duration relative to the tempo.

Delimiters:
OPENBRACK = {
Starts a definition
CLOSEDBRACK = }
Ends a definition 
NEWLINE = \n
Delimits parts of code
COMMA = ,
Separates groups of notes and chords or loops and segments

Literals:
INSTRUMENT_LITERAL = piano | guitar | horn | bass | snare | hihat
NOTE_LITERAL = [A-Ga-g][# + b]?[1-7]?
A note is a single, predefined frequency played by an instrument. In music, notes are letters A-G, they can be sharp, flat, or neither, and they can optionally have an octave.
CHORD_LITERAL = [A-Ga-g][# + b]?[1-7]?[minor]?
A chord is a predefined group of notes. Similar logic to notes applies, however chords can be major or minor. It is standard to assume the chord is major if not noted as minor.
TIME_LITERAL = [0-9]+ | [0-9]+ .? [0-9]+
This follows tempo and beat to describe an amount of time. Tempo is in beats per minute and beat is relative to the program’s tempo. It can be a whole number or float
DESCRIPTION_LITERAL = [a-zA-Z]+
A one word description to describe the desired chord to generate.
IDENTIFIER = [a-zA-Z][a-zA-Z0-9]*
Used to identify loops, segments, and groups
