/**
 * =====================================================
 * ARES UNIFIED VOICE SYSTEM
 * =====================================================
 * Single frontend that handles:
 * ✅ Voice recording & Whisper transcription
 * ✅ Desktop automation commands
 * ✅ AI conversation
 * ✅ Text-to-speech responses
 * 
 * All commands go through /ai-command endpoint
 * Backend handles routing to correct handler
 * =====================================================
 */

console.log("🚀 ARES Voice System Loading...");

// =====================================================
// GLOBAL STATE
// =====================================================
var ARES = {
    isRecording: false,
    mediaRecorder: null,
    audioChunks: [],
    audioStream: null,
    whisperAvailable: false,
    desktopAvailable: false,
    language: "en",
    userName: "Shobutik",
    voiceRate: 1.0,
    voicePitch: 1.0,
    voices: [],
    selectedVoice: null
};

// =====================================================
// INITIALIZATION
// =====================================================
document.addEventListener("DOMContentLoaded", function() {
    console.log("📄 Initializing ARES...");
    
    updateClock();
    setInterval(updateClock, 1000);
    
    checkSystemStatus();
    loadVoices();
    
    // Start reminder polling
    setInterval(checkReminders, 2000);
    
    // Space bar to toggle voice
    document.addEventListener('keydown', function(e) {
        if (e.code === 'Space' && e.target.tagName !== 'INPUT' && e.target.tagName !== 'TEXTAREA') {
            e.preventDefault();
            toggleVoice();
        }
    });
    
    console.log("✅ ARES Ready!");
});

// =====================================================
// REMINDER POLLING
// =====================================================
function checkReminders() {
    fetch("/reminders/triggered")
        .then(function(r) { return r.json(); })
        .then(function(data) {
            if (data.triggered && data.triggered.length > 0) {
                data.triggered.forEach(function(reminder) {
                    showReminderNotification(reminder);
                });
            }
        })
        .catch(function(e) {
            // Silent fail - server might be busy
        });
}

function showReminderNotification(reminder) {
    var icon = reminder.reminder_type === "alarm" ? "⏰" : 
               reminder.reminder_type === "timer" ? "⏱️" : "🔔";
    
    var message = icon + " " + reminder.message;
    
    // Show on screen
    showResponse(message, "success");
    
    // Speak it
    speak(reminder.message);
    
    // Play alarm sound for alarms/timers
    if (reminder.reminder_type === "alarm" || reminder.reminder_type === "timer") {
        playAlarmSound();
    }
    
    // Browser notification
    if ("Notification" in window && Notification.permission === "granted") {
        new Notification("ARES " + icon, {
            body: reminder.message,
            icon: "/static/icon.png"
        });
    }
}

function playAlarmSound() {
    // Play beeps for alarm
    try {
        var ctx = new (window.AudioContext || window.webkitAudioContext)();
        
        function beep(freq, startTime) {
            var osc = ctx.createOscillator();
            var gain = ctx.createGain();
            osc.connect(gain);
            gain.connect(ctx.destination);
            osc.frequency.value = freq;
            gain.gain.value = 0.3;
            osc.start(startTime);
            osc.stop(startTime + 0.2);
        }
        
        // Play 3 beeps
        beep(880, ctx.currentTime);
        beep(880, ctx.currentTime + 0.3);
        beep(880, ctx.currentTime + 0.6);
    } catch (e) {}
}

// Request notification permission
if ("Notification" in window && Notification.permission === "default") {
    Notification.requestPermission();
}

// =====================================================
// SYSTEM STATUS CHECK
// =====================================================
function checkSystemStatus() {
    fetch("/status")
        .then(function(r) { return r.json(); })
        .then(function(data) {
            ARES.whisperAvailable = data.features && data.features.whisper_available;
            ARES.desktopAvailable = data.features && data.features.desktop_automation;
            
            console.log("System Status:", data);
            
            var features = [];
            if (data.features && data.features.ai_brain) features.push("AI Brain ✅");
            if (ARES.whisperAvailable) features.push("Voice ✅");
            if (ARES.desktopAvailable) features.push("Desktop ✅");
            
            var msg = "Welcome, " + ARES.userName + "! 👋\n\n";
            msg += "ARES online: " + features.join(", ") + "\n\n";
            msg += "🎤 Click START LISTENING or press SPACE\n";
            msg += "⌨️ Or type commands below";
            
            showResponse(msg, "success");
        })
        .catch(function(e) {
            console.error("Status check failed:", e);
            showResponse("⚠️ Server not running?\n\nRun: python main_web.py", "error");
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
// VOICE TOGGLE
// =====================================================
function toggleVoice() {
    if (ARES.isRecording) {
        stopRecording();
    } else {
        startRecording();
    }
}

// =====================================================
// START RECORDING
// =====================================================
function startRecording() {
    console.log("🎤 Starting...");
    
    navigator.mediaDevices.getUserMedia({
        audio: {
            channelCount: 1,
            sampleRate: 16000,
            echoCancellation: true,
            noiseSuppression: true
        }
    })
    .then(function(stream) {
        ARES.audioStream = stream;
        
        var mimeType = 'audio/webm';
        if (!MediaRecorder.isTypeSupported(mimeType)) {
            mimeType = 'audio/ogg';
            if (!MediaRecorder.isTypeSupported(mimeType)) {
                mimeType = 'audio/mp4';
            }
        }
        
        ARES.mediaRecorder = new MediaRecorder(stream, { mimeType: mimeType });
        ARES.audioChunks = [];
        
        ARES.mediaRecorder.ondataavailable = function(e) {
            if (e.data.size > 0) ARES.audioChunks.push(e.data);
        };
        
        ARES.mediaRecorder.onstop = function() {
            console.log("🛑 Recording stopped");
            processRecording();
        };
        
        ARES.mediaRecorder.start(500);
        ARES.isRecording = true;
        
        updateVoiceButton(true);
        setCoreState("listening");
        setVisualizerActive(true);
        showTranscript("🎤 Listening... Click STOP when done.", false);
        playBeep(true);
    })
    .catch(function(e) {
        console.error("Mic error:", e);
        showResponse("❌ Cannot access microphone!\n\n" + e.message, "error");
    });
}

// =====================================================
// STOP RECORDING
// =====================================================
function stopRecording() {
    console.log("🛑 Stopping...");
    
    ARES.isRecording = false;
    updateVoiceButton(false);
    
    if (ARES.mediaRecorder && ARES.mediaRecorder.state !== "inactive") {
        ARES.mediaRecorder.stop();
    }
    
    if (ARES.audioStream) {
        ARES.audioStream.getTracks().forEach(function(t) { t.stop(); });
        ARES.audioStream = null;
    }
}

// =====================================================
// PROCESS RECORDING
// =====================================================
function processRecording() {
    if (ARES.audioChunks.length === 0) {
        showTranscript("No audio recorded.", false);
        setCoreState("idle");
        setVisualizerActive(false);
        return;
    }
    
    setCoreState("processing");
    setVisualizerActive(false);
    showTranscript("🔄 Transcribing...", false);
    showProcessing(true, "Processing audio...");
    
    var audioBlob = new Blob(ARES.audioChunks, { type: ARES.audioChunks[0].type });
    var formData = new FormData();
    formData.append('audio', audioBlob, 'recording.webm');
    
    fetch('/voice/transcribe?language=' + ARES.language, {
        method: 'POST',
        body: formData
    })
    .then(function(r) { return r.json(); })
    .then(function(data) {
        showProcessing(false);
        
        if (data.error) {
            showResponse("❌ Transcription failed: " + data.error, "error");
            setCoreState("idle");
            return;
        }
        
        var text = (data.text || "").trim();
        
        if (text) {
            console.log("✅ Heard:", text);
            showTranscript("✅ You: \"" + text + "\"", false);
            sendCommand(text);
        } else {
            showTranscript("🤔 No speech detected.", false);
            setCoreState("idle");
        }
    })
    .catch(function(e) {
        console.error("Whisper error:", e);
        showProcessing(false);
        showResponse("❌ Error transcribing. Is Whisper installed?", "error");
        setCoreState("idle");
    });
}

// =====================================================
// SEND COMMAND
// =====================================================
function sendCommand(textOverride) {
    var inputEl = document.getElementById("commandInput");
    var text = textOverride || (inputEl ? inputEl.value.trim() : "");
    
    if (!text) return;
    
    if (inputEl && !textOverride) inputEl.value = "";
    
    console.log("📤 Sending:", text);
    
    setCoreState("processing");
    showProcessing(true, "ARES is thinking...");
    showTranscript("Processing: \"" + text + "\"", false);
    
    fetch("/ai-command", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ command: text })
    })
    .then(function(r) { return r.json(); })
    .then(function(data) {
        console.log("📥 Response:", data);
        showProcessing(false);
        
        var response = data.reply || data.response || data.speech || "Done.";
        var responseClass = data.success === false ? "error" : "success";
        
        showResponse(response, responseClass);
        
        var speech = data.speech || response;
        speak(speech);
    })
    .catch(function(e) {
        console.error("Error:", e);
        showProcessing(false);
        showResponse("❌ Error: " + e.message, "error");
        speak("Sorry, something went wrong.");
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
    
    // Clean text
    var clean = text
        .replace(/[✅❌⚠️🎤🔊🖥️📁💬🔍📸🪟⏰🔋📱💡🌐📝📊🔇🔉]/g, "")
        .replace(/•/g, "")
        .replace(/\n+/g, " ")
        .trim();
    
    if (!clean) {
        setCoreState("idle");
        return;
    }
    
    window.speechSynthesis.cancel();
    setCoreState("speaking");
    
    var utterance = new SpeechSynthesisUtterance(clean);
    utterance.rate = ARES.voiceRate;
    utterance.pitch = ARES.voicePitch;
    utterance.volume = 1.0;
    
    if (ARES.selectedVoice) {
        utterance.voice = ARES.selectedVoice;
    }
    
    utterance.onend = function() { setCoreState("idle"); };
    utterance.onerror = function() { setCoreState("idle"); };
    
    window.speechSynthesis.speak(utterance);
}

function loadVoices() {
    if (!("speechSynthesis" in window)) return;
    
    function doLoad() {
        ARES.voices = window.speechSynthesis.getVoices();
        
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
}

// =====================================================
// UI UPDATE FUNCTIONS
// =====================================================
function updateVoiceButton(isRecording) {
    var btn = document.getElementById("voiceToggleBtn");
    var txt = document.getElementById("voiceToggleText");
    
    if (btn) btn.classList.toggle("active", isRecording);
    if (txt) txt.textContent = isRecording ? "STOP LISTENING" : "START LISTENING";
}

function setCoreState(state) {
    var core = document.getElementById("coreCenter");
    var status = document.getElementById("coreStatus");
    
    if (core) {
        core.classList.remove("listening", "speaking", "processing");
        if (state !== "idle") core.classList.add(state);
    }
    
    var map = {
        "idle": "IDLE",
        "listening": "LISTENING",
        "speaking": "SPEAKING",
        "processing": "THINKING"
    };
    
    if (status) status.textContent = map[state] || "IDLE";
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
    var txt = document.getElementById("processingText");
    
    if (box) box.classList.toggle("active", show);
    if (txt && text) txt.textContent = text;
}

function showResponse(text, type) {
    var el = document.getElementById("responseText");
    if (el) {
        el.textContent = text;
        el.style.color = type === "error" ? "#ff6464" :
                         type === "success" ? "#00ff88" : "#fff";
    }
}

// =====================================================
// QUICK COMMANDS
// =====================================================
function sendQuickCommand(text) {
    showTranscript("Quick: " + text, false);
    sendCommand(text);
}

function checkHealth() {
    sendCommand("system status");
}

// =====================================================
// AUDIO FEEDBACK
// =====================================================
function playBeep(start) {
    try {
        var ctx = new (window.AudioContext || window.webkitAudioContext)();
        var osc = ctx.createOscillator();
        var gain = ctx.createGain();
        
        osc.connect(gain);
        gain.connect(ctx.destination);
        
        osc.frequency.value = start ? 880 : 440;
        gain.gain.value = 0.1;
        
        osc.start();
        osc.stop(ctx.currentTime + 0.1);
    } catch (e) {}
}

// =====================================================
// SETTINGS
// =====================================================
function openSettings() {
    var modal = document.getElementById("settingsModal");
    if (modal) modal.classList.add("active");
}

function closeSettings() {
    var modal = document.getElementById("settingsModal");
    if (modal) modal.classList.remove("active");
}

function updateLanguage(lang) { ARES.language = lang; }
function updateVoice(idx) { if (ARES.voices[idx]) ARES.selectedVoice = ARES.voices[idx]; }
function updateSpeed(v) { ARES.voiceRate = parseFloat(v); var el = document.getElementById("speedValue"); if (el) el.textContent = v; }
function updatePitch(v) { ARES.voicePitch = parseFloat(v); var el = document.getElementById("pitchValue"); if (el) el.textContent = v; }
function testVoiceOutput() { speak("Hello " + ARES.userName + "! I am ARES. Voice is working!"); }
function testMicrophone() { showResponse("🎤 Click START LISTENING to test", "info"); }

// =====================================================
// EXPOSE GLOBAL FUNCTIONS
// =====================================================
window.toggleVoice = toggleVoice;
window.sendCommand = sendCommand;
window.sendQuickCommand = sendQuickCommand;
window.checkHealth = checkHealth;
window.openSettings = openSettings;
window.closeSettings = closeSettings;
window.updateLanguage = updateLanguage;
window.updateVoice = updateVoice;
window.updateSpeed = updateSpeed;
window.updatePitch = updatePitch;
window.testVoiceOutput = testVoiceOutput;
window.testMicrophone = testMicrophone;

console.log("✅ ARES Voice System Loaded!");