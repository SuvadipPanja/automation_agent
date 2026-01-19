/**
 * =====================================================
 * ARES VOICE ASSISTANT - WHISPER POWERED
 * =====================================================
 * Uses Whisper AI for accurate speech recognition!
 * Much better than browser speech recognition.
 * =====================================================
 */

console.log("🚀 ARES Voice (Whisper Edition) Loading...");

// =====================================================
// CONFIGURATION
// =====================================================
var ARES = {
    // State
    isRecording: false,
    whisperAvailable: false,
    
    // Audio recording
    mediaRecorder: null,
    audioChunks: [],
    audioStream: null,
    
    // Settings
    language: "en",
    
    // Voice output
    voiceRate: 1.0,
    voicePitch: 1.0,
    voices: [],
    selectedVoice: null,
    
    // User info (remembered!)
    userName: "Shobutik"  // We know your name now! 😊
};

// =====================================================
// INITIALIZATION
// =====================================================
document.addEventListener("DOMContentLoaded", function() {
    console.log("📄 Initializing ARES...");
    
    // Update clock
    updateClock();
    setInterval(updateClock, 1000);
    
    // Check Whisper availability
    checkWhisperStatus();
    
    // Load voices for TTS
    loadVoices();
    
    console.log("✅ ARES Ready!");
});

// =====================================================
// CHECK WHISPER STATUS
// =====================================================
function checkWhisperStatus() {
    fetch("/voice/status")
        .then(function(r) { return r.json(); })
        .then(function(data) {
            ARES.whisperAvailable = data.whisper_available;
            console.log("🎤 Whisper available:", ARES.whisperAvailable);
            
            if (ARES.whisperAvailable) {
                showResponse("✅ Welcome back, " + ARES.userName + "!\n\n" +
                            "🎤 Whisper AI is ready!\n\n" +
                            "Click 'START LISTENING' to speak.\n" +
                            "Whisper provides MUCH better accuracy than browser recognition!", "success");
            } else {
                showResponse("⚠️ Whisper not loaded yet.\n\n" +
                            "Run this in terminal first:\n" +
                            "python voice/whisper_engine.py\n\n" +
                            "Then restart the web server.", "info");
            }
        })
        .catch(function(e) {
            console.log("⚠️ Voice API check failed:", e);
            ARES.whisperAvailable = false;
        });
}

// =====================================================
// CLOCK
// =====================================================
function updateClock() {
    var now = new Date();
    var time = now.toLocaleTimeString("en-US", { hour12: false });
    var el = document.getElementById("timeDisplay");
    if (el) el.textContent = time;
}

// =====================================================
// MAIN TOGGLE FUNCTION
// =====================================================
function toggleVoice() {
    console.log("🔘 Toggle clicked, isRecording:", ARES.isRecording);
    
    if (ARES.isRecording) {
        stopRecording();
    } else {
        startRecording();
    }
}

// =====================================================
// START RECORDING
// =====================================================
async function startRecording() {
    console.log("🎤 Starting recording...");
    
    if (!ARES.whisperAvailable) {
        showResponse("⚠️ Whisper not available!\n\n" +
                    "Please run: python voice/whisper_engine.py\n" +
                    "Then restart the server.", "error");
        return;
    }
    
    try {
        // Request microphone access
        ARES.audioStream = await navigator.mediaDevices.getUserMedia({ 
            audio: {
                channelCount: 1,
                sampleRate: 16000,
                echoCancellation: true,
                noiseSuppression: true
            } 
        });
        
        console.log("✅ Microphone access granted");
        
        // Create MediaRecorder
        var mimeType = 'audio/webm';
        if (!MediaRecorder.isTypeSupported(mimeType)) {
            mimeType = 'audio/ogg';
            if (!MediaRecorder.isTypeSupported(mimeType)) {
                mimeType = 'audio/mp4';
            }
        }
        
        ARES.mediaRecorder = new MediaRecorder(ARES.audioStream, { mimeType: mimeType });
        ARES.audioChunks = [];
        
        ARES.mediaRecorder.ondataavailable = function(event) {
            if (event.data.size > 0) {
                ARES.audioChunks.push(event.data);
            }
        };
        
        ARES.mediaRecorder.onstop = function() {
            console.log("🛑 Recording stopped, processing...");
            processRecording();
        };
        
        // Start recording
        ARES.mediaRecorder.start(500); // Collect data every 500ms
        ARES.isRecording = true;
        
        // Update UI
        updateVoiceButton(true);
        setCoreState("listening");
        setVisualizerActive(true);
        showTranscript("🎤 Recording... Speak now!\n\nClick 'STOP LISTENING' when done.", false);
        showResponse("🎤 Whisper is listening, " + ARES.userName + "!\n\n" +
                    "Speak clearly, then click STOP.\n" +
                    "Whisper will transcribe accurately!", "info");
        
        // Play start sound
        speak("Listening");
        
    } catch(e) {
        console.error("❌ Microphone error:", e);
        showResponse("❌ Cannot access microphone!\n\n" + e.message + "\n\n" +
                    "Please allow microphone access:\n" +
                    "1. Click lock icon in address bar\n" +
                    "2. Allow microphone\n" +
                    "3. Refresh page", "error");
    }
}

// =====================================================
// STOP RECORDING
// =====================================================
function stopRecording() {
    console.log("🛑 Stopping recording...");
    
    ARES.isRecording = false;
    updateVoiceButton(false);
    
    if (ARES.mediaRecorder && ARES.mediaRecorder.state !== "inactive") {
        ARES.mediaRecorder.stop();
    }
    
    if (ARES.audioStream) {
        ARES.audioStream.getTracks().forEach(function(track) {
            track.stop();
        });
        ARES.audioStream = null;
    }
}

// =====================================================
// PROCESS RECORDING WITH WHISPER
// =====================================================
async function processRecording() {
    if (ARES.audioChunks.length === 0) {
        console.log("No audio recorded");
        setCoreState("idle");
        setVisualizerActive(false);
        showTranscript("No audio recorded. Try again!", false);
        return;
    }
    
    setCoreState("processing");
    setVisualizerActive(false);
    showTranscript("🧠 Whisper is transcribing...", false);
    showProcessing(true, "Transcribing with Whisper AI...");
    
    // Create audio blob
    var audioBlob = new Blob(ARES.audioChunks, { type: ARES.audioChunks[0].type });
    console.log("Audio blob size:", audioBlob.size, "bytes");
    
    // Create form data
    var formData = new FormData();
    formData.append('audio', audioBlob, 'recording.webm');
    
    try {
        console.log("📤 Sending to Whisper...");
        
        var response = await fetch('/voice/transcribe?language=' + ARES.language, {
            method: 'POST',
            body: formData
        });
        
        var data = await response.json();
        console.log("📥 Whisper response:", data);
        
        showProcessing(false);
        
        if (data.error) {
            console.error("Transcription error:", data.error);
            showResponse("❌ Transcription failed:\n\n" + data.error, "error");
            setCoreState("idle");
            return;
        }
        
        var text = data.text || "";
        
        if (text) {
            console.log("✅ Whisper heard:", text);
            showTranscript("✅ Whisper heard:\n\n\"" + text + "\"", false);
            
            // Send to AI
            sendToAI(text);
        } else {
            showTranscript("🤔 No speech detected.\n\nTry speaking louder or closer to mic.", false);
            showResponse("No speech detected.\n\nTips:\n• Speak louder\n• Get closer to microphone\n• Reduce background noise", "info");
            setCoreState("idle");
        }
        
    } catch(e) {
        console.error("❌ Whisper API error:", e);
        showProcessing(false);
        showResponse("❌ Error connecting to Whisper.\n\nMake sure the server is running.", "error");
        setCoreState("idle");
    }
}

// =====================================================
// SEND TO AI BACKEND
// =====================================================
function sendToAI(command) {
    console.log("📤 Sending to ARES AI:", command);
    
    setCoreState("processing");
    showProcessing(true, "ARES is thinking...");
    
    fetch("/ai-command", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ command: command })
    })
    .then(function(r) { return r.json(); })
    .then(function(data) {
        console.log("📥 ARES Response:", data);
        showProcessing(false);
        
        var response = data.reply || data.response || data.speech || "I received your command.";
        showResponse(response, "success");
        speak(response);
    })
    .catch(function(e) {
        console.error("❌ AI Error:", e);
        showProcessing(false);
        showResponse("❌ Error connecting to AI.\n\nIs the server running?", "error");
        speak("Sorry, I had trouble processing that.");
        setCoreState("idle");
    });
}

// =====================================================
// TEXT TO SPEECH
// =====================================================
function speak(text) {
    if (!text || !("speechSynthesis" in window)) {
        setCoreState("idle");
        return;
    }
    
    window.speechSynthesis.cancel();
    setCoreState("speaking");
    
    // Clean text (remove emojis)
    var cleanText = text.replace(/[\u{1F600}-\u{1F6FF}]/gu, "")
                       .replace(/[\u{2600}-\u{26FF}]/gu, "")
                       .replace(/[\u{2700}-\u{27BF}]/gu, "")
                       .replace(/[\u{1F900}-\u{1F9FF}]/gu, "")
                       .replace(/[•●○]/g, "")
                       .trim();
    
    if (!cleanText) {
        setCoreState("idle");
        return;
    }
    
    var utterance = new SpeechSynthesisUtterance(cleanText);
    utterance.rate = ARES.voiceRate;
    utterance.pitch = ARES.voicePitch;
    utterance.volume = 1.0;
    
    if (ARES.selectedVoice) {
        utterance.voice = ARES.selectedVoice;
    }
    
    utterance.onend = function() {
        console.log("🔊 Done speaking");
        setCoreState("idle");
    };
    
    utterance.onerror = function() {
        setCoreState("idle");
    };
    
    window.speechSynthesis.speak(utterance);
}

// =====================================================
// LOAD VOICES
// =====================================================
function loadVoices() {
    if (!("speechSynthesis" in window)) return;
    
    function doLoad() {
        ARES.voices = window.speechSynthesis.getVoices();
        console.log("🔊 Found " + ARES.voices.length + " voices");
        
        var select = document.getElementById("voiceSelect");
        if (select && ARES.voices.length > 0) {
            var html = "";
            for (var i = 0; i < ARES.voices.length; i++) {
                var v = ARES.voices[i];
                var isEnglish = v.lang.indexOf("en") === 0;
                var selected = (isEnglish && !ARES.selectedVoice) ? " selected" : "";
                if (selected) ARES.selectedVoice = v;
                html += '<option value="' + i + '"' + selected + '>' + v.name + ' (' + v.lang + ')</option>';
            }
            select.innerHTML = html;
        }
    }
    
    doLoad();
    speechSynthesis.onvoiceschanged = doLoad;
    setTimeout(doLoad, 500);
    setTimeout(doLoad, 1000);
}

// =====================================================
// UI UPDATE FUNCTIONS
// =====================================================
function updateVoiceButton(isRecording) {
    var btn = document.getElementById("voiceToggleBtn");
    var txt = document.getElementById("voiceToggleText");
    
    if (btn) {
        btn.classList.toggle("active", isRecording);
    }
    if (txt) {
        txt.textContent = isRecording ? "STOP LISTENING" : "START LISTENING";
    }
}

function setCoreState(state) {
    var core = document.getElementById("coreCenter");
    var status = document.getElementById("coreStatus");
    
    if (core) {
        core.classList.remove("listening", "speaking", "processing");
        if (state !== "idle") core.classList.add(state);
    }
    
    var statusMap = {
        "idle": "IDLE",
        "listening": "LISTENING",
        "speaking": "SPEAKING",
        "processing": "THINKING"
    };
    
    if (status) status.textContent = statusMap[state] || "IDLE";
}

function setVisualizerActive(active) {
    var viz = document.getElementById("voiceVisualizer");
    if (viz) viz.classList.toggle("visualizer-active", active);
}

function showTranscript(text, isInterim) {
    var el = document.getElementById("transcriptText");
    if (el) {
        el.textContent = text;
        el.classList.toggle("interim", isInterim);
    }
}

function showProcessing(show, text) {
    var box = document.getElementById("processingBox");
    var textEl = document.getElementById("processingText");
    
    if (box) box.classList.toggle("active", show);
    if (textEl && text) textEl.textContent = text;
}

function showResponse(text, type) {
    var el = document.getElementById("responseText");
    if (el) {
        el.textContent = text;
        el.style.color = type === "error" ? "#ff6464" : 
                         type === "success" ? "#00ff88" : 
                         type === "info" ? "#00d9ff" : "#fff";
    }
}

// =====================================================
// TEXT INPUT & QUICK COMMANDS
// =====================================================
function sendCommand() {
    var input = document.getElementById("commandInput");
    if (!input || !input.value.trim()) return;
    
    var text = input.value.trim();
    input.value = "";
    
    showTranscript("Typed: \"" + text + "\"", false);
    sendToAI(text);
}

function sendQuickCommand(text) {
    showTranscript("Quick command: \"" + text + "\"", false);
    sendToAI(text);
}

function checkHealth() {
    setCoreState("processing");
    showProcessing(true, "Checking system health...");
    
    fetch("/health")
        .then(function(r) { return r.json(); })
        .then(function(data) {
            showProcessing(false);
            var msg = "✅ System Health\n\n" +
                     "Agent: " + data.agent + "\n" +
                     "Status: " + data.status + "\n" +
                     "Time: " + data.time + "\n\n" +
                     "Whisper: " + (ARES.whisperAvailable ? "Ready ✅" : "Not loaded ⚠️");
            showResponse(msg, "success");
            speak("System is online and operational.");
            setCoreState("idle");
        })
        .catch(function() {
            showProcessing(false);
            showResponse("❌ Health check failed.", "error");
            setCoreState("idle");
        });
}

// =====================================================
// SETTINGS
// =====================================================
function openSettings() {
    var modal = document.getElementById("settingsModal");
    if (modal) modal.classList.add("active");
    loadVoices();
}

function closeSettings() {
    var modal = document.getElementById("settingsModal");
    if (modal) modal.classList.remove("active");
}

function updateWakeWord(enabled) {
    // Wake word handled by Whisper now
    console.log("Wake word setting:", enabled);
}

function updateLanguage(lang) {
    ARES.language = lang;
    console.log("Language set to:", lang);
}

function updateVoice(index) {
    if (ARES.voices[index]) {
        ARES.selectedVoice = ARES.voices[index];
        console.log("Voice set to:", ARES.selectedVoice.name);
    }
}

function updateSpeed(value) {
    ARES.voiceRate = parseFloat(value);
    var el = document.getElementById("speedValue");
    if (el) el.textContent = value;
}

function updatePitch(value) {
    ARES.voicePitch = parseFloat(value);
    var el = document.getElementById("pitchValue");
    if (el) el.textContent = value;
}

function testVoiceOutput() {
    speak("Hello " + ARES.userName + "! I am ARES, your AI assistant. Voice output is working correctly using Whisper for speech recognition!");
}

function testMicrophone() {
    showResponse("🎤 Testing microphone...\n\nClick START LISTENING and speak something!", "info");
}

// =====================================================
// EXPOSE GLOBAL FUNCTIONS
// =====================================================
window.toggleVoice = toggleVoice;
window.sendCommand = sendCommand;
window.sendQuickCommand = sendQuickCommand;
window.checkHealth = checkHealth;
window.openSettings = openSettings;
window.closeSettings = closeSettings;
window.updateWakeWord = updateWakeWord;
window.updateLanguage = updateLanguage;
window.updateVoice = updateVoice;
window.updateSpeed = updateSpeed;
window.updatePitch = updatePitch;
window.testVoiceOutput = testVoiceOutput;
window.testMicrophone = testMicrophone;

console.log("✅ ARES Voice (Whisper) Loaded!");