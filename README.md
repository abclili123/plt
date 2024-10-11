# plt project

Language summary:<br>

Lexical Grammar:<br>
Keywords:<br>
KEYWORD = define | tempo | play | generate | rest<br>
define: This keyword is used to define a part of the program, being a loop or segment<br>
tempo: This keyword is used to set the pace of the music<br>
play: This keyword is used to start playing a loop, segment, or group<br>
generate: This keyword is used to declare an AI generated chord. It is followed by a DESCRIPTION_LITERAL used to generate the chord<br>
<br>
Types:<br>
TYPE_PART = loop | segment<br>
loop and segment define parts of the program. loops are sequences of notes and chords that repeat. segments are the same but do not repeat.<br>
TYPE_GROUP = group<br>
group is used to chain parts (loops and segments) together so that they can be played easier<br>
TYPE_INSTRUMENT = instrument<br>
instrument is a reserved type used to denote that the next token is the instrument to be played in that part<br>
TYPE_SOUND = chord | note<br>
chord and note are types of sounds that instruments can play<br>
TYPE_TIME = beat <br>
beat describes the number as a duration relative to the tempo.<br>
<br>
Delimiters:<br>
OPENBRACK = {<br>
Starts a definition<br>
CLOSEBRACK = }<br>
Ends a definition <br>
NEWLINE = \n<br>
Delimits parts of code<br>
COMMA = ,<br>
Separates groups of notes and chords or loops and segments<br>

Literals:<br>
INSTRUMENT_LITERAL = piano | guitar | horn | bass | snare | hihat<br>
NOTE_LITERAL = [A-Ga-g][# + b]?[1-7]?<br>
A note is a single, predefined frequency played by an instrument. In music, notes are letters A-G, they can be sharp, flat, or neither, and they can optionally have an octave.<br>
CHORD_LITERAL = [A-Ga-g][# + b]?[1-7]?[minor]?<br>
A chord is a predefined group of notes. Similar logic to notes applies, however chords can be major or minor. It is standard to assume the chord is major if not noted as minor.<br>
TIME_LITERAL = [0-9]+ | [0-9]+ .? [0-9]+<br>
This follows tempo and beat to describe an amount of time. Tempo is in beats per minute and beat is relative to the program’s tempo. It can be a whole number or float<br>
DESCRIPTION_LITERAL = [a-zA-Z]+<br>
A one word description to describe the desired chord to generate.<br>
IDENTIFIER = [a-zA-Z][a-zA-Z0-9]*<br>
Used to identify loops, segments, and groups<br>
