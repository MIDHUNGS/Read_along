//webkitURL is deprecated but nevertheless
URL = window.URL || window.webkitURL;

var gumStream; 						//stream from getUserMedia()
var recorder; 						//WebAudioRecorder object
var input; 							//MediaStreamAudioSourceNode  we'll be recording
var encodingType; 					//holds selected encoding for resulting audio (file)
var encodeAfterRecord = true;       // when to encode

// shim for AudioContext when it's not avb. 
var AudioContext = window.AudioContext || window.webkitAudioContext;
var audioContext; //new audio context to help us record

var encodingTypeSelect = document.getElementById("encodingTypeSelect");
var recordButton = document.getElementById("recordButton");
var stopButton = document.getElementById("stopButton");

var mic_listening = document.getElementById("mic_listening_1");

var img1Show = document.getElementById("image-1");
var buttonContainer = document.getElementById("button-container");
var tryagainbutton = document.getElementById("try-again-button");
var nextbutton = document.getElementById("next-button");
var endbutton = document.getElementById("end-button");
var exitbutton = document.getElementById("exit-game");
var halfComplete = document.getElementById("word-ten-complete");
var imgid = document.getElementById("image-id");

var correctWord = document.getElementById("correct-word");
var wordName = document.getElementById("word-name");
var errorMessage = document.getElementById("error-message-full");
var errorDiv = document.getElementById("error-message");

var urlParams = new URLSearchParams(window.location.search);
var grade = urlParams.get('grade');

document.getElementById("grade").innerHTML = grade;


async function repeatImage() {
    for (let i = 0; i < img_list[grade].length; i++) {
        await firstRec(img_list[grade][i]);
        console.log(i);
    }
}

var ind = 0;
{
    var recCount = 0;
}
function firstRec(value) {
    recCount = 0;
    imgid.src = value[0];
    imgid.name = value[1];
    img1Show.style.display = "block";
    _rescursiveRec(recCount, value);
}

async function _rescursiveRec(recCount, value) {
    mic_listening.style.display = "block";
    const recorder = await recordAudio();
    recorder.start();
    await sleep(5000);
    const audio = await recorder.stop();
    mic_listening.style.display = "none";
    fetch("/feedback/save_audio/" + value[1], {
        method: "post",
        body: audio.audioBlob
    }).then(function (response) {
        return response.text();
    }).then(function (text) {
        fetch("/feedback/falign_result", {
            method: "post",
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ "audio_path": text, "target_phrase": value[1] })
        }).then(function (response) {
            return response.text();
        }).then(function (text) {
            const json_res = JSON.parse(text);
            if (json_res.data.status === "Error") {
                errorMessage.innerHTML = json_res.data.ExceptionMessage;
                errorDiv.style.display = "block";
                if (recCount < 2) {
                    recCount = recCount + 1;
                    var audioplay = new Audio('static/pictionary_speak_again.mp3');
                    audioplay.play();
                    audioplay.onended = function () {
                        buttonContainer.style.display = "block";
                        tryagainbutton.style.display = "inline-block";
                        if (ind === img_list[grade].length - 1) {
                            endbutton.style.display = "inline-block";
                        } else {
                            nextbutton.style.display = "inline-block";
                        }
                        if (ind === 9) {
                            halfComplete.style.display = "block";
                            exitbutton.style.display = "inline-block";
                        }
                    };
                } else {
                    if (ind === img_list[grade].length - 1) {
                        var audioplay = new Audio('static/pictionary_complete_activity.mp3');
                        audioplay.play();
                        audioplay.onended = function () {
                            correctWord.innerHTML = img_list[grade][ind][1];
                            wordName.style.display = "block";
                            buttonContainer.style.display = "block";
                            endbutton.style.display = "inline-block";
                        };
                    } else {
                        var audioplay = new Audio('static/pictionary_speak_again.mp3');
                        audioplay.play();
                        audioplay.onended = function () {
                            correctWord.innerHTML = img_list[grade][ind][1];
                            wordName.style.display = "block";
                            buttonContainer.style.display = "block";
                            nextbutton.style.display = "inline-block";
                            if (ind === 9) {
                                halfComplete.style.display = "block";
                                exitbutton.style.display = "inline-block";
                            }
                        };
                    }
                }
            } else {
                if (json_res.data.adjusted_word_score >= 0.5) {
                    if (ind === img_list[grade].length - 1) {
                        var audioplay = new Audio('static/pictionary_complete_activity.mp3');
                        audioplay.play();
                        audioplay.onended = function () {
                            correctWord.innerHTML = img_list[grade][ind][1];
                            wordName.style.display = "block";
                            buttonContainer.style.display = "block";
                            endbutton.style.display = "inline-block";
                        };
                    } else {
                        var audioplay = new Audio('static/pictionary_correct_word.mp3');
                        audioplay.play();
                        audioplay.onended = function () {
                            correctWord.innerHTML = img_list[grade][ind][1];
                            wordName.style.display = "block";
                            buttonContainer.style.display = "block";
                            nextbutton.style.display = "inline-block";
                            if (ind === 9) {
                                halfComplete.style.display = "block";
                                exitbutton.style.display = "inline-block";
                            }
                        };
                    }
                } else {
                    var audioplay = new Audio('static/' + img_list[grade][ind][1] + '_correct.mp3');
                    audioplay.play();
                    audioplay.onended = function () {
                        correctWord.innerHTML = img_list[grade][ind][1];
                        wordName.style.display = "block";
                        var audioplay = new Audio('static/pictionary_wrong_word.mp3');
                        audioplay.play();
                        audioplay.onended = function () {
                            buttonContainer.style.display = "block";
                            tryagainbutton.style.display = "inline-block";
                            if (ind === img_list[grade].length - 1) {
                                endbutton.style.display = "inline-block";
                            } else {
                                nextbutton.style.display = "inline-block";
                            }
                            if (ind === 9) {
                                halfComplete.style.display = "block";
                                exitbutton.style.display = "inline-block";
                            }
                        };
                    };
                }
            }
        });
    });
}

function showNextButton() {
    nextbutton.style.display = "block";
}

function showEndButton() {
    endbutton.style.display = "block";
}

tryagainbutton.addEventListener('click', () => {
    recCount = recCount + 1;
    _rescursiveRec(recCount, img_list[grade][ind]);
    tryagainbutton.style.display = "none";
    nextbutton.style.display = "none";
    endbutton.style.display = "none";
    exitbutton.style.display = "none";
    buttonContainer.style.display = "none";
    halfComplete.style.display = "none";
    wordName.style.display = "none";
    errorDiv.style.display = "none";
});

nextbutton.addEventListener('click', () => {
    ind = ind + 1;
    firstRec(img_list[grade][ind]);
    tryagainbutton.style.display = "none";
    nextbutton.style.display = "none";
    endbutton.style.display = "none";
    exitbutton.style.display = "none";
    buttonContainer.style.display = "none";
    halfComplete.style.display = "none";
    wordName.style.display = "none";
    errorDiv.style.display = "none";
});

endbutton.addEventListener('click', () => {
    fetch("/pictionary/end_score", {
        method: "get"
    }).then(function (response) {
        return response.text();
    }).then(function (text) {
        document.getElementById("score").innerHTML = text;
        document.getElementById("final-score").style.display = "block";
        tryagainbutton.style.display = "none";
        nextbutton.style.display = "none";
        endbutton.style.display = "none";
        exitbutton.style.display = "none";
        buttonContainer.style.display = "none";
        halfComplete.style.display = "none";
        wordName.style.display = "none";
        errorDiv.style.display = "none";
    });
});

exitbutton.addEventListener('click', () => {
    fetch("/pictionary/end_score", {
        method: "get"
    }).then(function (response) {
        return response.text();
    }).then(function (text) {
        document.getElementById("score").innerHTML = text;
        document.getElementById("final-score").style.display = "block";
        tryagainbutton.style.display = "none";
        nextbutton.style.display = "none";
        endbutton.style.display = "none";
        exitbutton.style.display = "none";
        buttonContainer.style.display = "none";
        halfComplete.style.display = "none";
        wordName.style.display = "none";
        errorDiv.style.display = "none";
    });
});


const recordAudio = () =>
    new Promise(async resolve => {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        const mediaRecorder = new MediaRecorder(stream);
        const audioChunks = [];

        mediaRecorder.addEventListener("dataavailable", event => {
            audioChunks.push(event.data);
        });

        const start = () => mediaRecorder.start();

        const stop = () =>
            new Promise(resolve => {
                mediaRecorder.addEventListener("stop", () => {
                    const audioBlob = new Blob(audioChunks);
                    const audioUrl = URL.createObjectURL(audioBlob);
                    const audio = new Audio(audioUrl);
                    const play = () => audio.play();
                    resolve({ audioBlob, audioUrl, play });
                });

                mediaRecorder.stop();
            });

        resolve({ start, stop });
    });

const sleep = time => new Promise(resolve => setTimeout(resolve, time));
