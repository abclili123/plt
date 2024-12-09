# plt project

### Team members:<br>
#### Dan Itzer, Liliana Seoror<br>

### Installation and Execution Instructions<br>
Ensure the lastest version of python3 is installed on your machine<br>
Ensure the build script has the proper permissions: ```chmod +x build.sh```<br>
You will also require Flask to be installed as the program is run on a local server<br>
```
pip install flask
```
<br>
In order to spin up a testing server (make sure you are in the project root directory)<br>

```
python3 app.py
```

or <br>
```
./build.sh
```
<br>

### Usage <br>
After starting up the local server, navigate to <a ref="http://127.0.0.1:5000">http://127.0.0.1:5000 </a> <br>
If you get a permissions error, clear cookies or reopen localhost in an incognito tab. <br>
Paste your example program in the far left textbox, then hit "play"<br>
Your program will then be compiled and translated into the corresponding sounds using the 
<a href="https://developer.mozilla.org/en-US/docs/Web/API/Web_Audio_API">Web Audio API </a> <br>
and be played through the browser.
<br>

### Context Free Grammar:
< program > → < tempo > < NEWLINE > < statement >*
<br>

< statement > → < define_part > OR < group > OR < play_statement >
<br>
 
< define_part > → < KEYWORD , define > < define_type > < IDENTIFIER > < OPENBRACK > < part_body > < CLOSEBRACK >
<br>

< define_type > → < TYPE_PART , {loop} > OR < TYPE_PART , {segment} >
<br>

< part_body > → < instrument_declaration > < sounds >*
<br>

< instrument_declaration > → < TYPE_INSTRUMENT > < INSTRUMENT_LITERAL > < NEWLINE >
<br>

< sounds > → < note_or_chord > (< COMMA > <note_or_chord>)* < duration >
		<br>OR < KEYWORD , rest > < duration >
		<br>OR < KEYWORD , generate >  < DESCRIPTION_LITERAL > (< TYPE_SOUND, {note} > OR < TYPE_SOUND, {chord} >) ( < COMMA > < DESCRIPTION_LITERAL > (< TYPE_SOUND, {note} > OR < TYPE_SOUND, {chord} >))* < duration >
		<br>OR < IDENTIFIER > < NEWLINE >
<br>

< note_chord > → < TYPE_SOUND, {note} > < NOTE_LITERAL > 
               <br>OR < TYPE_SOUND, {chord} > < CHORD_LITERAL >
<br>

< duration > → < TIME_LITERAL > < TYPE_TIME > < NEWLINE >
<br>
< tempo > → < KEYWORD , tempo > < TIME_LITERAL >
<br>

< play_statement > → < KEYWORD , play > < IDENTIFIER > (< COMMA > < IDENTIFIER >)* OR < KEYWORD , play > < define_type > < IDENTIFIER > OPENBRACK > <part_body> < CLOSEBRACK >
<br>

< group > → < TYPE_GROUP > < IDENTIFIER > OPENBRACK (< IDENTIFIER > (< COMMA > < IDENTIFIER >)* < NEWLINE > )* < CLOSEBRACK >
<br>

### Lexical Grammar:
#### Keywords:<br>
KEYWORD = define | tempo | play | generate | rest<br>
- define: This keyword is used to define a part of the program, being a loop or segment<br>
- tempo: This keyword is used to set the pace of the music<br>
- play: This keyword is used to start playing a loop, segment, or group<br>
- generate: This keyword is used to declare an AI generated chord. It is followed by a DESCRIPTION_LITERAL used to generate the chord<br>
<br>

#### Types:<br>
- TYPE_PART = loop | segment<br>
loop and segment define parts of the program. loops are sequences of notes chords, and/ or segments that repeat. segments are the same but do not repeat.<br>
- TYPE_GROUP = group<br>
group is used to chain parts (loops and segments) together so that they can be played easier<br>
- TYPE_INSTRUMENT = instrument<br>
instrument is a reserved type used to denote that the next token is the instrument to be played in that part<br>
- TYPE_SOUND = chord | note<br>
chord and note are types of sounds that instruments can play<br>
- TYPE_TIME = beat | beats <br>
beat describes the number as a duration relative to the tempo.<br>
<br>

#### Delimiters:<br>
- OPENBRACK = {<br>
Starts a definition<br>
- CLOSEBRACK = }<br>
Ends a definition <br>
- NEWLINE = \n<br>
Delimits parts of code<br>
- COMMA = ,<br>
Separates groups of notes and chords or loops and segments<br>

#### Literals:<br>
INSTRUMENT_LITERAL = piano | guitar | horn | bass | snare | hihat<br>
- NOTE_LITERAL = ```[A-Ga-g][# + b]?[1-7]?```<br>
A note is a single, predefined frequency played by an instrument. In music, notes are letters A-G, they can be sharp, flat, or neither, and they can optionally have an octave.<br>
- CHORD_LITERAL = ```[A-Ga-g][# + b]?[1-7]?[m]?```<br>
A chord is a predefined group of notes. Similar logic to notes applies, however chords can be major or minor. It is standard to assume the chord is major if not noted as minor.<br>
- TIME_LITERAL = ```[0-9]+ | [0-9]+ .? [0-9]+```<br>
This follows tempo and beat to describe an amount of time. Tempo is in beats per minute and beat is relative to the program’s tempo. It can be a whole number or float<br>
- DESCRIPTION_LITERAL = ```[a-zA-Z]+```<br>
A one word description to describe the desired chord to generate.<br>
- IDENTIFIER = ```[a-zA-Z][a-zA-Z0-9_]*```<br>
Used to identify loops, segments, and groups<br>

#### Example program descirptions:<br>
Example 1: how to make a drum kit<br>
This is a basic test of the lexer to make sure that we are reaching each delimiter and processing the tokens within those sections.
<br>

Example 2: how to have background music and a solo. The background loops and the solo plays once <br>
This is a test of multiple note declarations within a single expression, and how the lexer handles a handful of tokens within a delimiter segment.
<br>

Example 3: background piano, a guiatr part, and a drum kit all looping at the same time. <br>
This is test of more complex timings and whether the lexer can handle float/double types as well as special characters like '#' in token parsing.
<br>

Example 4: how to play mary had a little lamb. Each segment of the melody plays, then there is one beat of rest. the loop consists of segemnts with a loop, so when the loop is played the segments play in order and repeat.<br>
This test serves as a demonstration for a practical use case, as well as testing the control flow with identifers as each segment must be played in order within the loop defined after.
<br>

Example 5: Groups loops together to play easier. Similar to example 1. Plays the group and the loop at the same time so the output sound would be twinkle twinkle little start playing with drums in the bakcground. This file has errors to show how error tokens are handled. <br>
The purpose of this test is to make sure that the lexer can gracefully handle errors when encountered and continue to parse the rest of the program. The lexer should be able to constrain the error token within its respective delimiters, and the parsing of code outside those delimiters should not be affected. <br>

#### DFA of lexer:<br>
clicking image removes blur<br>
<img width="1383" alt="plt dfa" src="https://github.com/user-attachments/assets/43675d8d-74ab-4165-aab3-7938ca1029d4">


#### Video Tutorial:<br>
<a href="https://www.youtube.com/watch?v=Qz1vOPhSQWs">link to video </a> 


