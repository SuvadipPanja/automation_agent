// ================================
// ARES Frontend Controller
// ================================

// GLOBAL STATE
const statusEl = document.getElementById("status");
const responseBox = document.getElementById("responseBox");
const commandInput = document.getElementById("commandInput");

// ----------------
// STATUS HANDLER
// ----------------
function setStatus(text, cls = "idle") {
    statusEl.textContent = text;
    statusEl.className = "status " + cls;
}

// ----------------
// SEND TEXT COMMAND
// ----------------
function sendCommand() {
    const command = commandInput.value.trim();
    if (!command) return;

    responseBox.textContent = "ARES is thinking...\n";
    setStatus("THINKING", "thinking");

    fetch("/ai-command", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ command })
    })
    .then(res => res.json())
    .then(data => {
        responseBox.textContent = data.response || JSON.stringify(data, null, 2);
        setStatus("IDLE", "idle");
    })
    .catch(err => {
        responseBox.textContent = "ERROR:\n" + err;
        setStatus("ERROR", "error");
    });

    commandInput.value = "";
}

// ----------------
// VOICE INPUT (placeholder)
// ----------------
function sendVoice() {
    responseBox.textContent = "🎤 Voice input not enabled yet.";
}

// ----------------
// CONTROL BUTTONS
// ----------------
function checkHealth() {
    fetch("/health")
        .then(r => r.json())
        .then(d => responseBox.textContent = JSON.stringify(d, null, 2));
}

function loadTasks() {
    fetch("/tasks")
        .then(r => r.json())
        .then(d => responseBox.textContent = JSON.stringify(d, null, 2));
}

function loadSchedules() {
    fetch("/schedules")
        .then(r => r.json())
        .then(d => responseBox.textContent = JSON.stringify(d, null, 2));
}

function reloadSchedules() {
    fetch("/reload-schedules", { method: "POST" })
        .then(r => r.json())
        .then(d => responseBox.textContent = JSON.stringify(d, null, 2));
}

// ----------------
// ENTER KEY SUPPORT
// ----------------
commandInput.addEventListener("keydown", e => {
    if (e.key === "Enter") sendCommand();
});
