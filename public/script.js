import * as THREE from 'three';
import  { GLTFLoader } from './three/examples/jsm/loaders/GLTFLoader.js';
import { DRACOLoader } from './three/examples/jsm/loaders/DRACOLoader.js'
import { RGBELoader } from './three/examples/jsm/loaders/RGBELoader.js';
import { FBXLoader } from './three/examples/jsm/loaders/FBXLoader.js';
let nodes = {};
let isMicOn = true;
let lipsync;
let audio = null;
let lipAnim = false;
let mixer ;
let anim;
let controller;
let signal;
let scene;
let micPause = false;
let model;  
let morphTargetNames = []
let closedBtnclick = false;
let intialAudioPlaying = false;
let link = ""
let processingRequest = false;
let rand_num;
let wordsWithTiming;

let userId;
let finalTranscript = "";
let headMesh;
let currentType = detectDeviceType();


const match = {
    "a" : "viseme_aa",
    "E" : "viseme_E",
    "k" : "viseme_kk",
    "d" : "viseme_DD",
    "S" : "viseme_SS",
    "s" : "viseme_SS",
    "e" : "viseme_FF",
    "f" : "viseme_PP",
    "i" : "viseme_I",
    "o" : "viseme_O",
    "O" : "viseme_O",
    "u" : "viseme_U",
    "r" : "viseme_RR",
    "t" : "viseme_TH",
    "T" : "viseme_TH",
    "p" : "viseme_PP",
}

const states = document.getElementById('states');
const wave = document.getElementById('wave');
const waveform = document.getElementById('mic-overlay1');


function detectDeviceType() {
    const userAgent = navigator.userAgent.toLowerCase();

    if (/mobile|iphone|ipod|android|blackberry|mini|windows\sce|palm/i.test(userAgent)) {
        return "Phone";
    }
    if (/tablet|ipad|playbook|silk/i.test(userAgent)) {
        return "Tablet";
    }
    return "Desktop";
}

document.addEventListener("DOMContentLoaded", () => {
    window.parent.postMessage({ type: 'READY' }, '*');
     if(deviceType === 'Phone'){
        document.body.classList.add(deviceType); 
        const infoBoard = document.getElementById('info-board');
        infoBoard.src ="assets/infoPhone.png";
     }
});

window.addEventListener("resize", () => {
   if(currentType ==='Phone'){
       document.body.className = currentType; 
   }
});



const deviceType = detectDeviceType();
console.log(`You are using a: ${deviceType}`);


let currentIndex = 0;

function getQueryParams() {
    const urlParams = new URLSearchParams(window.location.search);
    return {
        id: urlParams.get('id'),
        assistant_name: urlParams.get("assistant_name"),
        company_name: urlParams.get("company_name")
    };
}

async function callAuthorizeAPI(local_user_id) {
    const parentOrigin = document.referrer || window.top.location.origin; 
    console.log({parentOrigin})
    let params = getQueryParams();

    if (!params.id || !parentOrigin) {
        console.error('Missing required parameters: id or url');
        return;
    }
    console.log({'paramId': params.id});
    console.log({'parenOrigin' : parentOrigin});
    console.log({'user_id' : local_user_id});
    try {
        const response = await fetch(`${link}/authorize`, {
            method: 'POST', 
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                id: params.id,
                url: parentOrigin,
                user_id : local_user_id,
            }), 
        });

        console.log({response});
        if (response.ok) {
            const data = await response.json();
            console.log('API Response:', data);
            return data;
        } else {
            console.error('Error in API request:', response.status);
        }
    } catch (error) {
        console.error('Error in fetch:', error);
    }
}

window.onload = function () {
    display3DModel(nodes); 
};



function display3DModel(nodes) {
    let overlay = document.getElementById('canvas-container');

    let width = window.innerWidth;
    let height = window.innerHeight;

    const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
    renderer.setSize(width , height);
    renderer.setPixelRatio(window.devicePixelRatio);
    renderer.setClearColor(0xff00ff, 0); 
    overlay.appendChild(renderer.domElement);

    scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(60,width/height, 0.01, 1000);
    camera.updateProjectionMatrix();

    
    const directionalLight2 = new THREE.DirectionalLight(0xffffff, 3); 
    directionalLight2.position.set(0,-0.5,2);
   // scene.add(directionalLight2);




    const ambientLight = new THREE.AmbientLight(0xffffff, 5); 
   // scene.add(ambientLight);


    const rgbeLoader = new RGBELoader();
rgbeLoader.load('./assets/back3.hdr', function (texture) {
    texture.mapping = THREE.EquirectangularReflectionMapping;
    scene.environment = texture;
   // scene.background = null; // Optional: Set HDR as background
});


   const loaderFbx = new FBXLoader();
/*
   const ktx2Loader = new THREE.KTX2Loader()
   .setTranscoderPath('./assets/basis/')
   .detectSupport(renderer);
   
   loader.setKTX2Loader(ktx2Loader);
   loader.setMeshoptDecoder(MeshoptDecoder);
   */
   const loader = new GLTFLoader();
   const dracoLoader = new DRACOLoader();
   dracoLoader.setDecoderPath('https://www.gstatic.com/draco/v1/decoders/'); 
   loader.setDRACOLoader(dracoLoader);
    loader.load('assets/model/HanaMetaModel.glb', function(gltf) {
        model = gltf.scene;
       

        loaderFbx.load('assets/model/brief.fbx', function (anim) {
            mixer = new THREE.AnimationMixer(model);
           console.log({anim});
            const action = mixer.clipAction(anim.animations[0]);
            action.play();
        });
        
        //for girl 
        if(deviceType === 'Phone'){
            model.scale.set(4.8,4.8,4.8); 
            model.position.set(0, -2.6, -4.5);
            model.rotation.x = Math.PI/12;
            camera.position.set(-0.1,4,3);
        }else{
            model.scale.set(0.016,0.016,0.016)                   // model.scale.set(0.017,0.017,0.017);                           // model.scale.set(1.2,1.2,1.2);                                       //  model.scale.set(0.95,0.95,0.95); 
            model.position.set(0, 0, -0.6);
            model.rotation.x = Math.PI/12;
            model.rotation.y = -Math.PI/30;
            camera.position.set(-0.1,1.35,2); //1.5
        }
    


        const box = new THREE.Box3().setFromObject(model);
        const center = box.getCenter(new THREE.Vector3());

       // model.position.set(0, 0, 0);
       // camera.position.set(0,1.2,1.7);
    
       // camera.lookAt(center);

        // Log blend shapes
         scene.add(model);
    
        
        model.traverse((child)=>{ 
              if(child.isMesh && child.morphTargetInfluences){
                   morphTargetNames = Object.keys(child.morphTargetDictionary);
                   console.log('Morph target detected', morphTargetNames);
              }
        })

        headMesh = model?.getObjectByName("Hana_FaceMesh");  //mesh_4 //Hana_FaceMesh //1
        setupBlinkAnimation();
        setUpEyeMovementAndSmile();
        
        mixer = new THREE.AnimationMixer(model);
        console.log({'anim' : gltf.animations})
       // anim = gltf.animations;


        //const specificClip = anim[1]; 
        //mixer.clipAction(specificClip).play();

        render();
        animate(nodes, mixer);
    });
    const clock = new THREE.Clock();
    function render(){
            requestAnimationFrame(render);
               if(mixer){
                    let delta = clock.getDelta();
                     mixer.update(delta);
             }
            renderer.render(scene, camera);
    }


    overlay = document.getElementById('canvasOverlay');
    window.addEventListener('resize', () => {
        const width = window.innerWidth;
        const height = window.innerHeight;
        renderer.setSize(width, height);
        camera.aspect = width / height;
        camera.updateProjectionMatrix();

        currentType = detectDeviceType();
      });

      
      document.addEventListener("contextmenu", function(event) {
        event.preventDefault();
      });

      document.addEventListener("mousedown", function(event) {
        event.preventDefault();
      });
      
      
        
let previousPhoneme = null;
let timeouts = []; 
function animate(nodes, mixer) {
    requestAnimationFrame(() => animate(nodes, mixer));

    if (audio && isMicOn) {
        let currentTime = audio.currentTime;

        // Find the current phoneme based on timing
        const currentPhoneme = wordsWithTiming.find(
            ({ start, end }) => currentTime >= start && currentTime < end
        );

        if (currentPhoneme && currentPhoneme !== previousPhoneme) {
            previousPhoneme = currentPhoneme;

            const { phonemes } = currentPhoneme;
            let phonemeArray = phonemes.split(""); 
            let delay = 0;

            timeouts.forEach(clearTimeout);
            timeouts = [];

            phonemeArray.forEach((phoneme, index) => {
                const timeout = setTimeout(() => {
                    const viseme = phonemeToMorph[phoneme];
                    const morphTargetIndex = headMesh.morphTargetDictionary?.[viseme];

                    if (morphTargetIndex !== undefined) {
                        headMesh.morphTargetInfluences[morphTargetIndex] = 0.5; //0.7

                        // Reset morph influence after 200ms
                        setTimeout(() => {
                            headMesh.morphTargetInfluences[morphTargetIndex] = 0;
                        }, 200);
                    }
                }, delay);

                delay += 300; // Add delay for the next phoneme animation
                timeouts.push(timeout);
            });
        }

        // Stop lip-sync if audio moves out of phoneme time range
        if (!currentPhoneme) {
            previousPhoneme = null;
            timeouts.forEach(clearTimeout);
            timeouts = [];
        }
    }
    if (mixer) {
        let delta = clock.getDelta();
        mixer.update(delta);
    }
    renderer.render(scene, camera);
}

animate(nodes , mixer);
}


function speechToText(callback) {
    const SpeechRecognition =
      window.SpeechRecognition || window.webkitSpeechRecognition;
  
    if (!SpeechRecognition) {
      throw new Error("SpeechRecognition is not supported in this browser.");
    }
  
    const recognition = new SpeechRecognition();
    recognition.lang = 'en-US';
    recognition.interimResults = true;
    recognition.continuous = true;
  
    let hasSpoken = false; 

    recognition.onstart = () => {
      console.log("Speech recognition started.");
    };
    
    recognition.onend = () => {
      console.log("Speech recognition stopped.");
      hasSpoken = false; 
     // recognition.start();
    };
    
    recognition.onresult = (event) => {
      let transcript = '';
      for (let i = 0; i < event.results.length; i++) {
        transcript += event.results[i][0].transcript;
        finalTranscript = transcript;
      }
    
      if (transcript !== "" && !hasSpoken && isMicOn) {
        hasSpoken = true; 
        waveform.src = "assets/user_waveform1.gif";
        waveform.style.display = 'flex';
        wave.style.display = 'flex';
        waveform.style.width = "60vw";
        states.style.display = 'none';
      }
      callback(transcript);
    };
      

    recognition.onerror = (event) => {
     // console.error("Speech Recognition Error:", event.error);
      callback("");
    };
  
    return {
      start: () => {
        console.log("Starting speech recognition...");
        recognition.start();
      },
      stop: () => {
        console.log("Stopping speech recognition...");
        recognition.stop();
      },
    };
  }


  function speechToTextPhone(callback) {
    let mediaRecorder;
    let socket;
    let hasSpoken = false; 
    return {
        start: () => {
            navigator.mediaDevices.getUserMedia({ audio: true }).then((stream) => {
                console.log({ stream });

                if (!MediaRecorder.isTypeSupported('audio/webm')) {
                    alert('Browser not supported');
                    return;
                }

                mediaRecorder = new MediaRecorder(stream, {
                    mimeType: 'audio/webm',
                });

                socket = new WebSocket('wss://api.deepgram.com/v1/listen', [
                    'token',
                    'cfeb8eea6d4fb21b94fecff4d35b766924298913',
                ]);

                socket.onopen = () => {
                    console.log({ event: 'onopen' });

                    mediaRecorder.addEventListener('dataavailable', async (event) => {
                        if (event.data.size > 0 && socket.readyState === 1) {
                            socket.send(event.data);

                              if (!hasSpoken && isMicOn) {
                                hasSpoken = true; 
                                waveform.src = "assets/user_waveform1.gif";
                                waveform.style.display = 'flex';
                                wave.style.display = 'flex';
                                waveform.style.width = "60vw";
                                states.style.display = 'none';
                              }
                        }
                    });

                    mediaRecorder.start(1500);
                    mediaRecorder.requestData();
                };

                socket.onmessage = async(message) => {
                    hasSpoken = false;
                    const received = JSON.parse(message.data);
                    const transcript = received.channel.alternatives[0]?.transcript || "";
                    if (transcript && received.is_final && !hasSpoken && isMicOn) {
                        finalTranscript += transcript + ' ';
                        console.log({finalTranscript});

                        console.log("speech end");
                        console.log({intialAudioPlaying});
                        if(!intialAudioPlaying){
                                states.style.display = 'flex';
                                waveform.style.display = 'none';
                                wave.style.display = 'none'; 
                                console.log('gone inside');
                                console.log({closedBtnclick , processingRequest , finalTranscript});
                                if (!closedBtnclick && !processingRequest && finalTranscript !== "") {
                                    console.log('speak called');
                                    states.textContent = 'Processing...'   
                                    speech.stop();
                                    await speak(finalTranscript);
                            }
                              
                            }else{
                                console.log("Intial Audio is already playing")
                            }

                        callback(finalTranscript);
                    }
                };

                socket.onclose = () => {
                    console.log({ event: 'onclose' });
                };

                socket.onerror = (error) => {
                    console.error({ event: 'onerror', error });
                };
            }).catch((error) => {
                console.error("Error accessing microphone:", error);
                callback("", error);
            });
        },

        stop: () => {
            if (mediaRecorder) {
                mediaRecorder.stop();
            }
            if (socket) {
                socket.close();
            }
            console.log("Speech recognition stopped.");
        },
    };
}

let speech;
if(deviceType !== 'Phone'){
    speech = speechToText((transcript, error) => {
        if (error) {
          console.error("Error:", error);
        } else {
          console.log("Transcript:", transcript);
        }
      });
}else{
    speech = speechToTextPhone((transcript, error) => {
        if (error) {
          console.error("Error:", error);
        } else {
          console.log("Transcript:", transcript);
        }
      });
}
  

let queue = Promise.resolve();

async function speak(transcript) {  
    queue = queue.then(async () => {
        const params = getQueryParams();
        console.log('ID:', params.id);
        console.log('transcript Final', transcript);
        const formData = new FormData();
        formData.append('transcript', transcript);
        formData.append('vector_id', params.id);
        formData.append('user_id', userId);
        formData.append('assistant_name' , params.assistant_name);
        formData.append('company_name', params.company_name);
        try {
            processingRequest = true;

            const response = await fetch(`${link}/getVoice`, {
                method: 'POST',
                body: formData,
                signal: signal,
            });


            if (!response.ok) {
                processingRequest = false;
                if(deviceType !== "Phone"){
                    myvad.start();
                }
                console.log('speech started 3');
                speech.start();
                throw new Error(`HTTP error! Status: ${response.status}`);
            }

            const data = await response.json();
            console.log(data);


            //redirection logic
            console.log({'redirect': data.redirection})
       
            if (data.redirection) {
                window.parent.postMessage(
                  { redirection: data.redirection },
                  "*"
                );
            }

            //form filling
            console.log({'name': data.name})
            console.log({'email': data.email})
            console.log({'subject': data.contact_subject});
            console.log({'contact_message': data.contact_message})

            if(data.name && data.email && data.contact_message){
                window.parent.postMessage(
                    { name: data.name , email : data.email ,contact_subject :data.contact_subject , contact_message : data.contact_message},
                    "*"
                  );
            }

            //submitting form 
            console.log({'submitting_details': data.submitting_details})
            if (data.submitting_details) {
                window.parent.postMessage(
                  { submitting_details: data.submitting_details },
                  "*"
                );
            }

            console.log({'audio': data.audio_base64});

            //for elevenlabs
            if (data.audio_base64) { 
                wordsWithTiming = wordsWithTimingAndPhonemes(data.alignment);
                console.log({wordsWithTiming});       
                if(isMicOn){
                    console.log('audio base564');
                    lipsyncAnimation(`data:audio/wav;base64,${data.audio_base64}`);
                }
            } else {
                console.log("No audio data available.");
            }

            //for unreal 
            if (data?.TaskStatus === 'completed') {
                try {
                    const response = await fetch(data.TimestampsUri);
                    if (!response.ok) {
                        throw new Error(`Failed to fetch timestamps: ${response.statusText}`);
                    }
                    let alignment = await response.json();
                    wordsWithTiming = wordsWithPhonemesAndTimingUnreal(alignment);
                    console.log({wordsWithTiming});
                    if(isMicOn){
                        lipsyncAnimation(data.OutputUri);
                    }
                } catch (error) {
                    console.error('Error processing lipsync generation:', error);
                }
            }
            

   
        } catch (error) {
            states.textContent = 'Listening...';
            processingRequest = false;
           // myvad.start();
            console.log('speech started 4');
            //speech.start();
            if (error.name === 'AbortError') {
                console.log('Speak request was aborted');
            } else {
                console.error('Error:', error);
            }
        }
    });
}



const phonemeToMorph = {
    "a": "a",  "b": "E", "c": "K", "d": "t", 
    "e": "e",  "f": "f", "g": "E", "h": "au", 
    "i": "i",  "j": "k", "k": "k", "l": "pi", 
    "m": "pa",  "n": "pa", "o": "O", "p": "e", 
    "q": "uO",  "r": "r", "s": "s", "t": "t", 
    "u": "u",  "v": "E", "w": "uo", "x": "kf", 
    "y": "i",  "z": "rf","1":"op","2": "u","3":"ee",
    "4":"oa","5":"aeo","6":"ES","7":"eea","8":"aeT",
    "9":"aei","0":"eo"
};


function wordToPhonemes(word) {
    let phonemeSequence = [];
    for (const char of word) {
        if (phonemeToMorph[char]) {
            phonemeSequence.push(phonemeToMorph[char]);
        }
    }
    return phonemeSequence.join(''); 
}


function setUpEyeMovementAndSmile() {
    if (headMesh) {
       
        const morph_left_look = headMesh.morphTargetDictionary?.['Look_leftLook_left'];
        const morph_right_look = headMesh.morphTargetDictionary?.['Look_right'];
        const morph_brows_up = headMesh.morphTargetDictionary?.['brows_up'];
        const morph_smile = headMesh.morphTargetDictionary?.['smile'];
        headMesh.morphTargetInfluences[morph_smile] = 0.8;
        headMesh.morphTargetInfluences[morph_brows_up] = 0;
        function moveEyes() {
            let lookDirection = Math.random() > 0.5 ? morph_left_look : morph_right_look;
            if (lookDirection !== undefined) {
                headMesh.morphTargetInfluences[lookDirection] = 1;
                setTimeout(() => {
                    headMesh.morphTargetInfluences[lookDirection] = 0;
                    setTimeout(moveEyes, 4000 + Math.random() * 2000); 
                }, 1000);
            }
        }

        moveEyes();
    }
}


function setupBlinkAnimation() {
    if (headMesh) {
        const morphTargetIndex = headMesh.morphTargetDictionary?.['blink'];
        if (morphTargetIndex !== undefined) {
            function blink() {
                headMesh.morphTargetInfluences[morphTargetIndex] = 1;      
                setTimeout(() => {
                    headMesh.morphTargetInfluences[morphTargetIndex] = 0;
                    setTimeout(blink, 3000);
                }, 200); 
            }

            blink();
        }
    }
}



function wordsWithPhonemesAndTimingUnreal(alignment) {
    const wordsWithPhonemesAndTiming = [];

    alignment.forEach(({ word, start, end }) => {
        wordsWithPhonemesAndTiming.push({
            word,
            phonemes: wordToPhonemes(word), 
            start,
            end,
        });
    });

    return wordsWithPhonemesAndTiming;
}

function wordsWithTimingAndPhonemes(alignment) {
    const { characters, character_start_times_seconds, character_end_times_seconds } = alignment;

    const wordsWithPhonemesAndTiming = [];
    let currentWord = '';
    let startTime = null;

    characters.forEach((char, i) => {
        if (char === ' ') {
            if (currentWord) {
                wordsWithPhonemesAndTiming.push({
                    word: currentWord,
                    phonemes: wordToPhonemes(currentWord),
                    start: startTime,
                    end: character_end_times_seconds[i - 1], 
                });
                currentWord = '';
                startTime = null;
            }
        } else {
            if (!currentWord) {
                startTime = character_start_times_seconds[i]; 
            }
            currentWord += char;
        }
    });

    if (currentWord) {
        wordsWithPhonemesAndTiming.push({
            word: currentWord,
            phonemes: wordToPhonemes(currentWord),
            start: startTime,
            end: character_end_times_seconds[characters.length - 1],
        });
    }

    return wordsWithPhonemesAndTiming;
}


async function lipsyncAnimation(audioUrl) {
    audio = new Audio(audioUrl);
    console.log({audio})
    console.log({headMesh});
    if (!headMesh) {
        console.error("headMesh not found in the model.");
        return;
    }
    audio.play();

    audio.addEventListener('play', () => {
            waveform.style.display = 'flex';
            wave.style.display = 'flex';
            waveform.src = "assets/chatbot_wavform1.gif";
            waveform.style.width = "60vw";
            states.style.display = 'none';
 
          
            let arr = [0, 3,4];
            rand_num = arr[Math.floor(Math.random() * arr.length)];
            console.log(rand_num);

            const morph_brows_up = headMesh.morphTargetDictionary?.['brows_up'];
            if (morph_brows_up !== undefined) {
                headMesh.morphTargetInfluences[morph_brows_up] = 1;
                setTimeout(() => {
                    headMesh.morphTargetInfluences[morph_brows_up] = 0;
                }, 800);
            }

           setTimeout(()=>{     
            const morph_smile = headMesh.morphTargetDictionary?.['smile'];
            headMesh.morphTargetInfluences[morph_smile] = 0.2;
           // const specificClip = anim[rand_num]; 
           // mixer.clipAction(anim[1]).stop();
           // mixer.clipAction(anim[1]).setEffectiveTimeScale(0.5);
           // mixer.clipAction(specificClip).play();
            console.log('Audio playback has started (play event triggered).');
           },1500);
    });
    
    audio.addEventListener('ended', () => {
        console.log('audio ended');

        const morph_smile = headMesh.morphTargetDictionary?.['smile'];
        const morph_brows_up = headMesh.morphTargetDictionary?.['brows_up'];
        headMesh.morphTargetInfluences[morph_brows_up] = 0;
        headMesh.morphTargetInfluences[morph_smile] = 0.8;
      //  const specificClip = anim[1]; 
      //  mixer.clipAction(anim[rand_num]).stop();
      //  mixer.clipAction(specificClip).play();

        
       // if(anim && mixer){
      //      console.log('anim')
     //   }

        finalTranscript = "";
        processingRequest = false;
        intialAudioPlaying = false; 

        setTimeout(()=>{
            waveform.style.display = 'none';
            wave.style.display = 'none';
            states.style.display = 'flex';
            states.textContent = 'Listening...';
        },100);
        if(deviceType !== "Phone"){
            myvad.start();
        }
        console.log('speech started 1');
        speech.start();
    }); 
}

           let myvad = null;
           async function toggleCanvasOverlay() {
            try {
                const overlay = document.getElementById('box');
                console.log("waiting for model load");
                await waitForHeadMesh();
                states.style.display = 'flex';
                states.textContent = 'Listening...'

                const isOverlayVisible = overlay.style.display === 'flex';
                if (!isOverlayVisible) {
                    if (deviceType !== "Phone") {
                        console.log('Initializing VAD for non-phone device');
                
                        myvad = await vad.MicVAD.new({
                            positiveSpeechThreshold: 0.65,
                            minSpeechFrames: 8,
                            preSpeechPadFrames: 10,
                            onSpeechStart: () => {},
                            onFrameProcessed: (probs) => {},
                            onSpeechEnd: async () => {
                                if (deviceType !== 'Phone') {
                                    console.log("Speech ended");
                                    console.log({ intialAudioPlaying });
                
                                    if (!intialAudioPlaying) {
                                        states.style.display = 'flex';
                                        waveform.style.display = 'none';
                                        wave.style.display = 'none';
                                        console.log('Processing speech...');
                                        console.log({ closedBtnclick, processingRequest, finalTranscript });
                
                                        if (!closedBtnclick && !processingRequest) {
                                            states.textContent = 'Processing...';
                                            speech.stop();
                                            await speak(finalTranscript);
                                        }
                                    } else {
                                        console.log("Initial audio is already playing");
                                    }
                                }
                            },
                        });
                
                        console.log("VAD loaded");
                        window.myvad = myvad;
                
                        window.toggleVAD = async () => {
                            console.log("Running toggleVAD");
                            if (!myvad.listening) {
                                myvad.start();
                                speech.stop();
                                console.log("VAD is running");
                                intialAudioPlaying = true;
                
                                waveform.style.display = 'none';
                                wave.style.display = 'none';
                                states.style.display = 'flex';
                                states.textContent = 'Introducing...';
                                intialBtn.style.display = 'none';
                                window.parent.postMessage("expandIframe", "*");
                                await speak("Introduce yourself in just 2 lines.");
                            } else {
                                myvad.pause();
                                speech.stop();
                                console.log("VAD is paused");
                            }
                        };
                
                        window.toggleVAD();
                    } else {
                        console.log("Skipping VAD for phones");
                        speech.stop();
                        intialAudioPlaying = true;
                
                        waveform.style.display = 'none';
                        wave.style.display = 'none';
                        states.style.display = 'flex';
                        states.textContent = 'Introducing...';
                        intialBtn.style.display = 'none';
                        window.parent.postMessage("expandIframe", "*");
                        await speak("Introduce yourself in just 2 lines.");
                    }
                } else {
                    if (window.myvad) {
                        window.myvad.pause();
                        speech.stop();
                        console.log("VAD is paused");
                    }
                }
                overlay.style.display = isOverlayVisible ? 'none' : 'flex';
                

            } catch (e) {
                console.error("Failed:", e);
            }
        }


function waitForHeadMesh() {
    return new Promise((resolve) => {
            const checkHeadMesh = setInterval(() => {
                if (typeof headMesh !== "undefined") { 
                    clearInterval(checkHeadMesh);
                    resolve();
            }
        }, 100); // Check every 100ms
    });
}
// Event listener for the Open Canvas button
const infoBtn = document.getElementById('info');
const infoBoard = document.getElementById('info-board');
const infoImg = document.getElementById('info-img');
const btnsTagInfo = document.getElementsByClassName('btns-tag')[0];

infoBtn.addEventListener('click', () => {
    if (infoBoard.style.display === 'block') {
        infoImg.src = "assets/chat.png";
        infoBoard.style.display = 'none';
        btnsTagInfo.style.width = "80%";
        btnsTagInfo.style.height = "80%";
        btnsTagInfo.style.boxShadow = "";


    } else {
        infoImg.src = "assets/chat2.png";
        infoBoard.style.display = 'block';
        btnsTagInfo.style.boxShadow = "0 0 10px 10px rgba(105, 195, 15, 0.35)";
        btnsTagInfo.style.width = "95%";
        btnsTagInfo.style.height = "95%";
    }
});

const intialBtn = document.getElementById("intial-btn");
const intialImg = document.getElementById('intial-img');
const bgPad = document.getElementById('rounded-box');


const video = document.getElementById("video");
async function initWebcam() {
    console.log('intialize')
    const stream = await navigator.mediaDevices.getUserMedia({ video: true });
    video.srcObject = stream;
}

function initSocket(userId){
         //video capture -

  const ws = new WebSocket(`ws://127.0.0.1:8000/ws?user_id=${userId}`);
  let currentToolCallId = null;
  
  // Trigger image capture as soon as WebSocket connection is established
  ws.onopen = () => {
      console.log("WebSocket connected, starting image capture.");
      captureAndSend();  // Start sending images immediately
  };
  
  // Capture and send images continuously
  function captureAndSend() {
      console.log('captureAndSend');
      const canvas = document.createElement("canvas");
      canvas.width = video.videoWidth;
      canvas.height = video.videoHeight;
      canvas.getContext("2d").drawImage(video, 0, 0);
      const imageData = canvas.toDataURL("image/jpeg");
  
      ws.send(JSON.stringify({
          type: "image",
          tool_call_id: currentToolCallId,
          image: imageData
      }));
  
      setTimeout(captureAndSend, 3000);  
  }
  ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      if (data.type === "capture_image") {
          currentToolCallId = data.tool_call_id;  
          captureAndSend();  
      }
  };
  
}

intialBtn.addEventListener('click', async ()=>{
        let local_user_id = "";
        try {  
            intialBtn.disabled = true;
            intialImg.src = "assets/loader2.gif";
            intialImg.style.width = "50%";
            intialImg.style.height = "50%";
            if(deviceType === 'Phone'){
               // bgPad.src = 'assets/pad2.png';
                speech.start();
                speech.stop();
            }
            
            window.parent.postMessage({ type: 'GET_USER_ID' }, '*');
            window.addEventListener('message', (event) => {
                if (event.data && event.data.type === 'USER_ID_RESPONSE') {
                    local_user_id = event.data.userId;
                }
            });
            


        
            const data = await callAuthorizeAPI(local_user_id);
            console.log({data})
    
            userId = data.user_id;

            //memory management
            if(local_user_id === ""){
                 window.parent.postMessage({ type: 'STORE_USER_ID', userId }, '*'); 
            }

            if (data) {
                const stateManagement = document.getElementById('state-management');
                stateManagement.style.display = 'flex';
                closedBtnclick = false;
                initWebcam();
                initSocket(data.user_id);
                toggleCanvasOverlay();
            } else {
               console.warn('Authorization failed or no data received.');
            }
        
            controller = new AbortController();
            signal = controller.signal;
                
    
        } catch (error) {
            console.error('Error during the process:', error);
        }finally{
            intialBtn.disabled = false;
        }
});






// Get the mic overlay element
const micOverlay = document.getElementById("mic-overlay2");
let mediaStream = null; 
function muteMic() {
    if (mediaStream) {
        console.log("Microphone muted");
        mediaStream.getAudioTracks().forEach(track => {
            track.enabled = false;  
        });
    }
}

function unmuteMic() {
    if (mediaStream) {
        console.log("Microphone unmuted");
        mediaStream.getAudioTracks().forEach(track => {
            track.enabled = true; 
        });
    }
}


function muteMicCompletely() {
    if (mediaStream) {
        mediaStream.getAudioTracks().forEach(track => {
            track.stop(); 
        });
        console.log("Microphone fully stopped");
        mediaStream = null; 
    }
}

async function unmuteMicCompletely() {
    try {
        mediaStream = await navigator.mediaDevices.getUserMedia({ audio: true });
        console.log("Microphone re-enabled");
    } catch (err) {
        console.error("Failed to access microphone again:", err);
    }
}



// Event listener to toggle mic on click
const mic = document.getElementById('mic');
const btnsTagMic = document.getElementById('openBtn');
btnsTagMic.addEventListener('click', () => {
    console.log("Before toggle:", isMicOn);
    
    if (isMicOn) {
        muteMic();
        muteMicCompletely();
        mic.src = "assets/Mic_off.png";
        btnsTagMic.style.width = "80%";
        btnsTagMic.style.height = "80%";
        bgPad.style.display = 'none';
        btnsTagMic.style.boxShadow = "none";
        waveform.style.display = 'none';
        wave.style.display = 'none';
        states.style.display = 'none';
        processingRequest = false;
       if(deviceType !== 'Phone'){
           myvad.pause();
       }
        speech.stop();

        if(audio){
            audio.pause();
            audio.src = ""; 
            audio.remove(); 
            audio = null;
        }

     //   const specificClip = anim[1]; 
      //  console.log({rand_num});
     //   mixer.clipAction(anim[rand_num]).stop();
     //  mixer.clipAction(specificClip).play();
        console.log('Audio playback has started (play event triggered).');

        controller.abort();
        console.log("vad is stopped")

    } else {
        unmuteMic();
        unmuteMicCompletely();
        bgPad.style.display = 'block';

        mic.src = "assets/micOpen.png";
        btnsTagMic.style.boxShadow = "0 0 10px 10px rgba(105, 195, 15, 0.35)";
        btnsTagMic.style.width = "95%";
        btnsTagMic.style.height = "95%";
        waveform.style.display = 'none';
        wave.style.display = 'none';
        states.style.display = 'flex';
        states.textContent = 'Listening...'
        intialAudioPlaying = false;
        if(deviceType !== 'Phone'){
            myvad.start();
        }
        console.log('speech started 2');
        speech.start();
 
        controller = new AbortController();
        signal = controller.signal;
        console.log("vad is started")
    }

    isMicOn = !isMicOn; // Toggle the variable
    console.log("After toggle:", isMicOn);
});

const closeBtn = document.getElementById("closeBtn");
closeBtn.addEventListener('click', async () => {
    closedBtnclick = true; 
    console.log('closess');
    window.parent.postMessage("contractIframe", "*");
     
        toggleCanvasOverlay();
        intialBtn.style.display = 'flex';
        intialImg.src = "assets/CHAT_BOT_1x.png";
        intialImg.style.width = "100%";
        intialImg.style.height = "100%";
        if (audio) {
            audio.pause();
            audio.src = ""; 
            audio.remove();   
            audio = null;
            muteMicCompletely();

        }
    
    if(!isMicOn){
        bgPad.style.display = 'block';

        mic.src = "assets/micOpen.png";
        btnsTagMic.style.boxShadow = "0 0 10px 10px rgba(105, 195, 15, 0.35)";
        btnsTagMic.style.width = "95%";
        btnsTagMic.style.height = "95%";
        waveform.style.display = 'none';
        wave.style.display = 'none';
        states.style.display = 'flex';
        states.textContent = 'Listening...'
        intialAudioPlaying = false;
        if(deviceType !== 'Phone'){
            myvad.start();
        }
        console.log('speech started 2');
        speech.start();
    }
    
    
    

    isMicOn = true; 
  //  const specificClip = anim[1]; 
  //  mixer.clipAction(anim[rand_num]).stop();
  //  mixer.clipAction(specificClip).play();
    console.log('Audio playback has started (play event triggered).');
    if(deviceType !== 'Phone'){
        myvad.pause();
    }
    speech.stop();
    controller.abort();

    try {
        const response = await fetch(`${link}/removeUserId?user_id=${userId}`, {method: 'GET'});

        if (response.ok) {
            const result = await response.json();
            console.log("API Response:", result);
        } else {
            console.error("Failed to remove user ID:", response.statusText);
        }
    } catch (error) {
        console.error("Error calling API:", error);
    }

});

