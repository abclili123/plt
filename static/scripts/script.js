// audio set up vars
var audioCtx;
var globalAnalyser;
var globalGain;
var noteFrequencies;

const loops = {
    bass_guitar: [
        { instrument: 'bass', note: 'C', duration: 1 } // Single note
    ],
    bass_drums: [
        // Simultaneous notes
        { instrument: 'bass', note: ['A', 'B'], duration: 1 }, 
        // Sequential note
        { instrument: 'bass', note: 'A', duration: 1 } 
    ],
    hat: [
        { instrument: 'hihat', note: 'B', duration: 1 } // Single note
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
        const time = startTime;

        if (Array.isArray(step.note)) {
            // Play simultaneous notes
            step.note.forEach(note => {
                const frequency = noteFrequencies[`${note}4`]; // Default octave
                instruments[step.instrument](frequency, beatDuration, time);
            });
        } else {
            // Play single note
            const frequency = noteFrequencies[`${step.note}4`]; // Default octave
            instruments[step.instrument](frequency, beatDuration, time);
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

    // define usable instruments
}

function play(){
    initAudio();
    playGroup('drum_kit', 120); // Tempo = 120 BPM
}

// everything above this is boiler plate and will be in every program
function playNote(note, duration = 0.5, timeOffset = 0) {
    if (!noteFrequencies[note]) {
        console.error(`Note ${note} not found in frequency map.`);
        return;
    }

    const frequency = noteFrequencies[note];

    // we would create different oscs for each instrument keyword 
    // move this into the 'define usable instruments' comment
    const oscillator = audioCtx.createOscillator(); // Create oscillator
    oscillator.type = 'sine'; // Choose waveform type: sine, square, triangle, sawtooth
    oscillator.connect(globalGain);

    // Start and stop the oscillator
    // we would generate these lines of code from the play statements
    // calculating timeOffset and duration from tempo and beats and rests
    oscillator.frequency.setValueAtTime(frequency, audioCtx.currentTime + timeOffset);
    oscillator.start(audioCtx.currentTime + timeOffset);
    oscillator.stop(audioCtx.currentTime + timeOffset + duration);

    // alternatively we can generate arrays of data we can pass to functions to execute
    // the notes playing
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