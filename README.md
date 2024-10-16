# plt project

Team members:<br>
Dan Itzer, Liliana Seoror<br>

Installation and Execution Instructions<br>
Ensure the any version of python3 is installed on your machine<br>
Ensure the build script has the proper permissions: chmod +x build.sh<br>
Run the script as ./build.sh <input_filename> <output_filename> <br>

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
loop and segment define parts of the program. loops are sequences of notes chords, and/ or segments that repeat. segments are the same but do not repeat.<br>
TYPE_GROUP = group<br>
group is used to chain parts (loops and segments) together so that they can be played easier<br>
TYPE_INSTRUMENT = instrument<br>
instrument is a reserved type used to denote that the next token is the instrument to be played in that part<br>
TYPE_SOUND = chord | note<br>
chord and note are types of sounds that instruments can play<br>
TYPE_TIME = beat | beats <br>
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
CHORD_LITERAL = [A-Ga-g][# + b]?[1-7]?[m]?<br>
A chord is a predefined group of notes. Similar logic to notes applies, however chords can be major or minor. It is standard to assume the chord is major if not noted as minor.<br>
TIME_LITERAL = [0-9]+ | [0-9]+ .? [0-9]+<br>
This follows tempo and beat to describe an amount of time. Tempo is in beats per minute and beat is relative to the program’s tempo. It can be a whole number or float<br>
DESCRIPTION_LITERAL = [a-zA-Z]+<br>
A one word description to describe the desired chord to generate.<br>
IDENTIFIER = [a-zA-Z][a-zA-Z0-9_]*<br>
Used to identify loops, segments, and groups<br>

Example program descirptions:<br>
example 1: how to make a drum kit<br>
example 2: how to have background music and a solo. The background loops and the solo plays once
example 3: background piano, a guiatr part, and a drum kit all looping at the same time
example 4: how to play mary had a little lamb. Each segment of the melody plays, then there is one beat of rest. the loop consists of segemnts with a loop, so when the loop is played the segments play in order and repeat. 
example 5: Groups loops together to play easier. Similar to example 1. Plays the group and the loop at the same time so the output sound would be twinkle twinkle little start playing with drums in the bakcground. This file has errors to show how error tokens are handled. 
