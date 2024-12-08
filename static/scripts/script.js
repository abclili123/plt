// audio set up vars
var audioCtx;
var globalAnalyser;
var globalGain;
let noteFrequencies;
let chordFrequencies;

const loops = {
    bass_guitar: [
        { instrument: 'bass', sounds: ['note C', 'chord B'], duration: 1 },  // Note + Chord together
        { instrument: 'bass', sounds: 'rest', duration: 1 },  // Rest
        { instrument: 'bass', sounds: 'note G', duration: 1 },  // Single note
        { instrument: 'bass', sounds: 'chord A', duration: 1 }  // Single chord
    ],
    bass_drums: [
        { instrument: 'bass', sounds: ['note A', 'note B'], duration: 1 }, // Simultaneous notes
        { instrument: 'bass', sounds: 'note A', duration: 1 } // Sequential note
    ],
    hat: [
        { instrument: 'hihat', sounds: 'note B', duration: 1 } // Single note
    ]
};

// Define groups for simultaneous or sequential playback
const groups = {
    drum_kit: [
        ['bass_guitar', 'hat'], // Simultaneous playback
        'hat',                  // Sequential playback
        'bass_drums'            // Sequential playback
    ]
};

instruments = {
    bass: (frequency, duration, time) => {
        const oscillator = audioCtx.createOscillator();
        oscillator.type = 'sawtooth'; // Example bass sound
        oscillator.frequency.setValueAtTime(frequency, time);

        const gainNode = audioCtx.createGain();
        gainNode.gain.setValueAtTime(0.5, time); // Set volume
        gainNode.gain.exponentialRampToValueAtTime(0.001, time + duration);

        oscillator.connect(gainNode);
        gainNode.connect(globalGain);

        oscillator.start(time);
        oscillator.stop(time + duration);
    },
    hihat: (frequency, duration, time) => {
        const oscillator = audioCtx.createOscillator();
        oscillator.type = 'triangle'; // Example hi-hat sound
        oscillator.frequency.setValueAtTime(frequency, time);

        const gainNode = audioCtx.createGain();
        gainNode.gain.setValueAtTime(0.1, time); // Softer volume for hi-hat
        gainNode.gain.exponentialRampToValueAtTime(0.001, time + duration);

        oscillator.connect(gainNode);
        gainNode.connect(globalGain);

        oscillator.start(time);
        oscillator.stop(time + duration);
    }
}; 

function playGroup(groupName, tempo, startTime = audioCtx.currentTime) {
    const group = groups[groupName];
    console.log('Playing group:', groupName, 'with structure:', group);

    if (!group) {
        console.error(`Group "${groupName}" is not defined.`);
        return;
    }

    if (!Array.isArray(group)) {
        console.error(`Group "${groupName}" is not defined as an array.`);
        return;
    }

    group.forEach(loopName => {
        if (Array.isArray(loopName)) {
            loopName.forEach(innerLoopName => {
                if (loops[innerLoopName]) {
                    playLoop(innerLoopName, tempo, startTime);
                } else {
                    console.error(`Loop "${innerLoopName}" is not defined.`);
                }
            });
        } else {
            if (loops[loopName]) {
                playLoop(loopName, tempo, startTime);
                startTime += calculateLoopDuration(loopName, tempo);
            } else {
                console.error(`Loop "${loopName}" is not defined.`);
            }
        }
    });
}


function calculateLoopDuration(loopName, tempo) {
    const beatDuration = 60 / tempo;
    const loop = loops[loopName];

    return loop.reduce((totalDuration, step) => totalDuration + (step.duration || 1) * beatDuration, 0);
}

function playLoop(loopName, tempo, startTime = audioCtx.currentTime) {
    const loop = loops[loopName];
    const beatDuration = 60 / tempo; // Duration of one beat in seconds

    loop.forEach(step => {
        let time = startTime;

        // Check for 'rest'
        if (step.sounds === 'rest') {
            // Skip playing any sound during a rest, just increment time
            time += step.duration * beatDuration;
            return;  // Exit this iteration of the loop and move to the next step
        }

        // Handle other sound types (notes and chords)
        if (Array.isArray(step.sounds)) {
            // Play simultaneous sounds (notes or chords)
            step.sounds.forEach(sound => {
                if (sound.startsWith('note')) {
                    const note = sound.split(' ')[1];
                    const frequency = noteFrequencies[`${note}4`]; // Default octave is 4
                    instruments[step.instrument](frequency, beatDuration, time);
                } else if (sound.startsWith('chord')) {
                    const chord = sound.split(' ')[1];
                    if (chordFrequencies[chord]) {
                        chordFrequencies[chord].forEach(frequency => {
                            instruments[step.instrument](frequency, beatDuration, time);
                        });
                    } else {
                        console.error(`Chord "${chord}" is not defined.`);
                    }
                }
            });
        } else {
            // Play a single note or chord
            if (step.sounds.startsWith('note')) {
                const note = step.sounds.split(' ')[1];
                const frequency = noteFrequencies[`${note}4`]; // Default octave is 4
                instruments[step.instrument](frequency, beatDuration, time);
            } else if (step.sounds.startsWith('chord')) {
                const chord = step.sounds.split(' ')[1];
                if (chordFrequencies[chord]) {
                    chordFrequencies[chord].forEach(frequency => {
                        instruments[step.instrument](frequency, beatDuration, time);
                    });
                } else {
                    console.error(`Chord "${chord}" is not defined.`);
                }
            }
        }

        // Increment startTime for the next step
        startTime += step.duration * beatDuration;
    });
}

// def frequencies for notes
function generateFrequencyMap() {
    // Notes with sharps and flats
    const noteNames = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B'];
    const flatEquivalents = {
        'C#': 'Db',
        'D#': 'Eb',
        'F#': 'Gb',
        'G#': 'Ab',
        'A#': 'Bb'
    };

    const frequencyMap = {};
    const A4 = 440; // Reference frequency for A4
    const A4Index = noteNames.indexOf('A') + (4 * 12); // Index of A4

    for (let octave = 0; octave <= 7; octave++) {
        for (let i = 0; i < noteNames.length; i++) {
            const noteIndex = i + (octave * 12);
            const stepsFromA4 = noteIndex - A4Index;
            const frequency = A4 * Math.pow(2, stepsFromA4 / 12);
            const noteName = `${noteNames[i]}${octave}`;

            // Add sharp note
            frequencyMap[noteName] = parseFloat(frequency.toFixed(2));

            // Add flat equivalent if it exists
            if (flatEquivalents[noteNames[i]]) {
                const flatName = `${flatEquivalents[noteNames[i]]}${octave}`;
                frequencyMap[flatName] = parseFloat(frequency.toFixed(2));
            }

            // Stop at G7
            if (noteName === 'G7') break;
        }
    }

    return frequencyMap;
}

function generateChordMap() {
    const chordMap = {};

    // Chord intervals for major and minor
    const chordIntervals = {
        'maj': [0, 4, 7], // Major: Root, Major Third, Perfect Fifth
        'm': [0, 3, 7],   // Minor: Root, Minor Third, Perfect Fifth
    };

    // Notes with natural, sharp, and flat notes
    const noteNames = ['A', 'A#', 'B', 'C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#'];

    // Iterate over each note from A to G
    noteNames.forEach(rootNote => {
        // Generate major and minor chords for octaves 1 to 7
        for (let octave = 1; octave <= 7; octave++) {
            Object.keys(chordIntervals).forEach(chordType => {
                const intervals = chordIntervals[chordType];
                const chordName = `${rootNote}${chordType === 'maj' ? '' : chordType}${octave}`;

                // Find the root note's frequency
                const rootFrequency = noteFrequencies[rootNote + octave];  // Example: 'A4', 'C5'

                // Create an array to store the frequencies for the chord
                const chordFrequencies = intervals.map(interval => {
                    const noteIndex = noteNames.indexOf(rootNote) + interval;
                    const wrappedIndex = (noteIndex + 12) % 12;  // Wrap around to avoid negative indexes
                    const noteName = noteNames[wrappedIndex];
                    const frequency = noteFrequencies[noteName + octave];
                    return frequency;
                });

                // Store the chord frequencies in the chord map
                chordMap[chordName] = chordFrequencies;
            });
        }
    });

    return chordMap;
}

// audio set up
function initAudio() {
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
}

var maxAlltime = 0
function peak() {
    globalAnalyser.fftSize = 2048;
    var bufferLength = globalAnalyser.frequencyBinCount;
    var dataArray = new Uint8Array(bufferLength);
    globalAnalyser.getByteTimeDomainData(dataArray);

    //values range 0-255, over the range -1,1, so we find the max value from a frame, and then scale
    var maxValue = (dataArray.reduce((max, curr) => (curr > max ? curr : max)) - 128) / 127.0;
    //console.log(maxValue);
    if (maxValue > maxAlltime){
        maxAlltime = maxValue;
        //console.log("New record! -> " + maxAlltime);
    }
    requestAnimationFrame(peak);
}

function play(){
    initAudio();
    playGroup('drum_kit', 120); // Tempo = 120 BPM
}

document.getElementById('compile').addEventListener('click', function() {
    const code = document.getElementById('coding').value;
    
    // Send a POST request to the Flask backend
    fetch('/compile', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ code: code })
    })
    .then(response => response.json())
    .then(data => {
        lexer = data.lexer;
        parser = data.parser;
        generated_code = data.generated_code;

        document.getElementById("lexer-output").innerHTML = lexer;
        document.getElementById("parser-output").innerHTML = parser;
        document.getElementById("code-gen-output").innerHTML = generated_code;
    })
    .catch(error => console.error('Error:', error));
});