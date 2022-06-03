//webkitURL is deprecated but nevertheless
URL = window.URL || window.webkitURL;

var gumStream;                                          //stream from getUserMedia()
var recorder;                                           //WebAudioRecorder object
var input;                                                      //MediaStreamAudioSourceNode  we'll be recording
var encodingType;                                       //holds selected encoding for resulting audio (file)
var encodeAfterRecord = true;       // when to encode

// shim for AudioContext when it's not avb. 
var AudioContext = window.AudioContext || window.webkitAudioContext;
var audioContext; //new audio context to help us record

var encodingTypeSelect = document.getElementById("encodingTypeSelect");
var recordButton = document.getElementById("recordButton");
var stopButton = document.getElementById("stopButton");
var mic_listening = document.getElementById("mic_listening");

//add events to those 2 buttons
recordButton.addEventListener("click", startRecording);
stopButton.addEventListener("click", stopRecording);

function startRecording() {
        console.log("startRecording() called");

        /*
                Simple constraints object, for more advanced features see
                https://addpipe.com/blog/audio-constraints-getusermedia/
        */
    
    var constraints = { audio: true, video:false }

    /*
        We're using the standard promise based getUserMedia() 
        https://developer.mozilla.org/en-US/docs/Web/API/MediaDevices/getUserMedia
        */

        navigator.mediaDevices.getUserMedia(constraints).then(function(stream) {
                __log("getUserMedia() success, stream created, initializing WebAudioRecorder...");

                /*
                        create an audio context after getUserMedia is called
                        sampleRate might change after getUserMedia is called, like it does on macOS when recording through AirPods
                        the sampleRate defaults to the one set in your OS for your playback device

                */
                audioContext = new AudioContext();

                //update the format 
                document.getElementById("formats").innerHTML="Format: 1 channel "+encodingTypeSelect.options[encodingTypeSelect.selectedIndex].value+" @ "+audioContext.sampleRate/1000+"kHz"

                //assign to gumStream for later use
                gumStream = stream;
                
                /* use the stream */
                input = audioContext.createMediaStreamSource(stream);
                
                //stop the input from playing back through the speakers
                //input.connect(audioContext.destination)

                //get the encoding 
                encodingType = encodingTypeSelect.options[encodingTypeSelect.selectedIndex].value;
                
                //disable the encoding selector
                encodingTypeSelect.disabled = true;

                recorder = new WebAudioRecorder(input, {
                    workerDir: "static/js/", // must end with slash
                    encoding: encodingType,
                    numChannels:1, //2 is the default, mp3 encoding supports only 2
                    onEncoderLoading: function(recorder, encoding) {
                      // show "loading encoder..." display
                      __log("Loading "+encoding+" encoder...");
                    },
                    onEncoderLoaded: function(recorder, encoding) {
                      // hide "loading encoder..." display
                      __log(encoding+" encoder loaded");
                    }
                  });
  
                  recorder.onComplete = function(recorder, blob) { 
                          __log("Encoding complete");
                          createDownloadLink(blob,recorder.encoding);
                          encodingTypeSelect.disabled = false;
                  }
  
                  recorder.setOptions({
                    timeLimit:300,
                    encodeAfterRecord:encodeAfterRecord,
                ogg: {quality: 0.5},
                mp3: {bitRate: 160}
              });
  
                  //start the recording process
                  recorder.startRecording();
  
                   __log("Recording started");
  
          }).catch(function(err) {
                  //enable the record button if getUSerMedia() fails
          recordButton.disabled = false;
          mic_listening.style.display = "none";
          stopButton.disabled = true;
  
          });
  
          //disable the record button
      recordButton.disabled = true;
      mic_listening.style.display = "block";
      stopButton.disabled = false;
  }
  
  function stopRecording() {
          console.log("stopRecording() called");
          
          //stop microphone access
          gumStream.getAudioTracks()[0].stop();
  
          //disable the stop button
          stopButton.disabled = true;
          recordButton.disabled = false;
          mic_listening.style.display = "none";
          
          //tell the recorder to finish the recording (stop recording + encode the recorded audio)
          recorder.finishRecording();
  
          __log('Recording stopped');
  }
  
  function createDownloadLink(blob,encoding) {
          document.getElementById("recordingsTable").style = "display:block";
          var recordingList1 = document.getElementById("recordingsList");
          var url = URL.createObjectURL(blob);
          var au = document.createElement('audio');
          var tr = document.createElement('tr');
          var td1 = document.createElement('td');
          //      var td2 = document.createElement('td');
                  var td3 = document.createElement('td');
                  td3.setAttribute('style', 'width:370px');
                  // var li = document.createElement('li');
                  var link = document.createElement('a');
                  var radioInput = document.createElement('input');
                  radioInput.setAttribute('type', 'radio');
                  radioInput.setAttribute('style', 'height:25px;width:25px; float:left');
                  radioInput.setAttribute('name', 'select_audio');
          
                  //add controls to the <audio> element
                  au.controls = true;
                  au.src = url;
          
                  //link the a element to the blob
                  link.href = url;
                  link.download = new Date().toISOString() + '.'+encoding;
                  link.innerHTML = link.download;
          
                  radioInput.setAttribute('value', link.download);
                  //radioInput.setAttribute('checked', true);
          
                  //add the new audio and a elements to the li element
                  //li.appendChild(au);
                  //li.appendChild(link);
                  //li.appendChild(radioInput);
                  td3.appendChild(au);
                  td1.appendChild(radioInput);
                  tr.appendChild(td1);
                  tr.appendChild(td3);

        //add the li element to the ordered list
        //recordingsList.appendChild(li);
        recordingList1.appendChild(tr);
}



//helper function
function __log(e, data) {
        log.innerHTML += "\n" + e + " " + (data || '');
}
            