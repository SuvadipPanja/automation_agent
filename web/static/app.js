// =====================
// ARES UI CONTROLLER
// =====================

// ---- DOM ELEMENTS ----
const statusEl = document.getElementById("status");
const responseBox = document.getElementById("responseBox");
const inputEl = document.getElementById("commandInput");

// Safety check
if (!statusEl || !responseBox || !inputEl) {
    console.error("ARES UI ERROR: Missing required DOM elements");
}

// =====================
// STATUS HANDLING
// =====================
function setStatus(state) {
    if (!statusEl) return;
    statusEl.textContent = state;
    statusEl.className = "status " + state.toLowerCase();
}

// =====================
// 🔊 TEXT TO SPEECH
// =====================
function speak(text) {
    if (!("speechSynthesis" in window)) return;
    if (!text) return;

    const utterance = new SpeechSynthesisUtterance(text);
    utterance.rate = 0.95;
    utterance.pitch = 1.0;
    utterance.volume = 1.0;

    window.speechSynthesis.cancel();
    window.speechSynthesis.speak(utterance);
}

// =====================
// SYSTEM CONTROLS
// =====================
function checkHealth() {
    setStatus("THINKING");

    fetch("/health")
        .then(r => r.json())
        .then(d => {
            responseBox.textContent = JSON.stringify(d, null, 2);
            speak("System is online.");
            setStatus("IDLE");
        })
        .catch(err => {
            responseBox.textContent = "Health check failed.";
            setStatus("ERROR");
        });
}

function loadTasks() {
    setStatus("THINKING");

    fetch("/tasks")
        .then(r => r.json())
        .then(d => {
            if (!Array.isArray(d)) {
                responseBox.textContent = JSON.stringify(d, null, 2);
            } else {
                responseBox.textContent =
                    "Available tasks:\n\n" +
                    d.map(t => "• " + (t.name || t)).join("\n");
            }
            speak("Tasks loaded.");
            setStatus("IDLE");
        })
        .catch(() => {
            responseBox.textContent = "Failed to load tasks.";
            setStatus("ERROR");
        });
}

function loadSchedules() {
    setStatus("THINKING");

    fetch("/schedules")
        .then(r => r.json())
        .then(d => {
            responseBox.textContent = JSON.stringify(d, null, 2);
            speak("Schedules loaded.");
            setStatus("IDLE");
        })
        .catch(() => {
            responseBox.textContent = "Failed to load schedules.";
            setStatus("ERROR");
        });
}

function reloadSchedules() {
    setStatus("THINKING");

    fetch("/reload-schedules", { method: "POST" })
        .then(() => {
            responseBox.textContent = "Schedules reloaded.";
            speak("Schedules reloaded.");
            setStatus("IDLE");
        })
        .catch(() => {
            responseBox.textContent = "Reload failed.";
            setStatus("ERROR");
        });
}

// =====================
// 🧠 TEXT COMMAND
// =====================
function sendCommand(textOverride = null) {
    const cmd = textOverride || inputEl.value.trim();
    if (!cmd) return;

    setStatus("THINKING");
    responseBox.textContent = "ARES processing...\n\n" + cmd;

    fetch("/ai-command", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ command: cmd })
    })
        .then(r => r.json())
        .then(d => {
            // Normalize response
            if (d.reply) {
                responseBox.textContent = d.reply;
                speak(d.reply);
            } else {
                responseBox.textContent = JSON.stringify(d, null, 2);
                if (d.speech) speak(d.speech);
            }
            inputEl.value = "";
            setStatus("IDLE");
        })
        .catch(err => {
            responseBox.textContent = "ARES error: " + err;
            setStatus("ERROR");
        });
}

// =====================
// 🎙 VOICE INPUT
// =====================
function sendVoice() {
    const SpeechRecognition =
        window.SpeechRecognition || window.webkitSpeechRecognition;

    if (!SpeechRecognition) {
        responseBox.textContent = "Speech recognition not supported.";
        return;
    }

    const recognition = new SpeechRecognition();
    recognition.lang = "en-US";
    recognition.interimResults = false;
    recognition.maxAlternatives = 1;

    setStatus("LISTENING");
    responseBox.textContent = "ARES listening… 🎙";

    recognition.onresult = (event) => {
        const text = event.results[0][0].transcript;
        responseBox.textContent = "Heard: " + text;
        speak("Command received.");
        sendCommand(text);
    };

    recognition.onerror = (event) => {
        responseBox.textContent = "Voice error: " + event.error;
        speak("I did not understand.");
        setStatus("IDLE");
    };

    recognition.onend = () => {
        setStatus("IDLE");
    };

    recognition.start();
}

// =====================
// EXPOSE TO HTML
// =====================
window.checkHealth = checkHealth;
window.loadTasks = loadTasks;
window.loadSchedules = loadSchedules;
window.reloadSchedules = reloadSchedules;
window.sendCommand = sendCommand;
window.sendVoice = sendVoice;
