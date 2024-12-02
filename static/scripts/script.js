// audio set up vars
var audioCtx;
var globalAnalyser;
var globalGain;
var frequencies;

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
    frequencies = generateFrequencyMap();

    // define usable instruments
}

document.addEventListener("DOMContentLoaded", function(event) {
    initAudio();
});

// everything above this is boiler plate and will be in every program
function playNote(note, duration = 0.5, timeOffset = 0) {
    if (!frequencies[note]) {
        console.error(`Note ${note} not found in frequency map.`);
        return;
    }

    const frequency = frequencies[note];

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
{
    

    window.addEventListener('keydown', keyDown, false);
    window.addEventListener('keyup', keyUp, false);

    activeOscillators = {}
    activeGain = {}
    activeAM = {}
    let totalOsc = 0

    function keyDown(event) {
        const key = (event.detail || event.which).toString();
        if (keyboardFrequencyMap[key] && !activeOscillators[key]) {
            playNote(key);
        }
    }

    function keyUp(event) {
        const key = (event.detail || event.which).toString();
        if (keyboardFrequencyMap[key] && activeOscillators[key]) {
            activeGain[key].gain.exponentialRampToValueAtTime(0.0001, audioCtx.currentTime + .5)
            activeGain[key].gain.setTargetAtTime(0, audioCtx.currentTime, 1)
            if(keyboardFrequencyMap[key] && activeAM[key]){
                activeAM[key].gain.exponentialRampToValueAtTime(0.0001, audioCtx.currentTime + .5)
                activeAM[key].gain.setTargetAtTime(0, audioCtx.currentTime, 1)
                delete activeAM[key];
            }
            let arr = activeOscillators[key]
            let l = arr.length
            for(let i=0; i<l; i++){
                arr.pop().stop(audioCtx.currentTime+0.6)
                totalOsc -= 1
            }
            delete activeOscillators[key];
            delete activeGain[key];
        }
    }

    function playNote(key) {
        const gainNode = audioCtx.createGain();
        gainNode.connect(globalGain)
        gainNode.gain.setValueAtTime(0, audioCtx.currentTime);
        gainNode.gain.setTargetAtTime(0.5, audioCtx.currentTime, 1);

        let oscs = []
        totalOsc += 1
        oscs[0] = audioCtx.createOscillator();
        oscs[0].type = document.getElementById('wave').value
        oscs[0].frequency.setValueAtTime(keyboardFrequencyMap[key], audioCtx.currentTime)
        oscs[0].connect(gainNode)
        oscs[0].start();

        let activateLfo = document.getElementById('lfo').checked
        if(activateLfo){
            const lfo = audioCtx.createOscillator();
            lfo.frequency.value = 15;
            lfoGain = audioCtx.createGain();
            lfoGain.gain.value = 50;
            lfo.connect(lfoGain).connect(oscs[0].frequency);
            lfo.start();
        }

        // initiate AM
        let yesAm = document.getElementById('yesAm').checked
        let am = document.getElementById('am').value
        if(yesAm){
            const modulatorFreq = audioCtx.createOscillator();
            modulatorFreq.frequency.value = am;
            const depth = audioCtx.createGain();
            depth.gain.setValueAtTime(0, audioCtx.currentTime);
            depth.gain.setTargetAtTime(0.5, audioCtx.currentTime, 1);
            gainNode.gain.setTargetAtTime(1.0 - depth.gain.value, audioCtx.currentTime, 1);
            modulatorFreq.connect(depth).connect(gainNode.gain)
            modulatorFreq.start();
            activeAM[key] = depth
        }

        //initiate FM if checked
        let fm = document.getElementById('fm').value
        let modulationIndex = audioCtx.createGain();
        let fmInd = document.getElementById('fmInd').value
        if(fm>0){
            const fmFreq = audioCtx.createOscillator();
            modulationIndex.gain.value = fmInd;
            fmFreq.frequency.value = fm;
            fmFreq.connect(modulationIndex);
            modulationIndex.connect(oscs[0].frequency)
            fmFreq.start();
        }

        // initiate additive synthesis if checked
        let additive = document.getElementById('additive').value;
        if(additive > 0) {
            for (let i = 1; i <= additive; i++) {
                totalOsc += 1
                oscs[i] = audioCtx.createOscillator();
                oscs[i].type = document.getElementById('wave').value
                oscs[i].frequency.setValueAtTime(keyboardFrequencyMap[key] * i, audioCtx.currentTime)
                if (i > 0 && i < 3) {
                    oscs[i].frequency.setValueAtTime(keyboardFrequencyMap[key] * i + (Math.random() * 15), audioCtx.currentTime)
                } else if (i >= 3) {
                    oscs[i].frequency.setValueAtTime(keyboardFrequencyMap[key] * i - (Math.random() * 15), audioCtx.currentTime)
                }
                if (fm > 0) {
                    modulationIndex.connect(oscs[i].frequency)
                }
                oscs[i].connect(gainNode)
                oscs[i].start();
            }
        }

        globalGain.gain.setTargetAtTime(0.8/totalOsc, audioCtx.currentTime, 1);

        activeOscillators[key] = oscs
        activeGain[key] = gainNode
    }
});