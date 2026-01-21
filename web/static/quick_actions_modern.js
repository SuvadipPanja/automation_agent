/**
 * =====================================================
 * ARES QUICK ACTIONS - MODERN ARCHITECTURE
 * =====================================================
 * 
 * Routes all commands through unified /command endpoint
 * which intelligently routes to appropriate backend service
 * 
 * Architecture:
 * Button Click → /command endpoint → ARES Manager → Service Layer
 * 
 * =====================================================
 */

// =====================================================
// QUICK ACTION DEFINITIONS
// =====================================================

const QUICK_ACTIONS = {
    // System & Info
    "time": { label: "Time", emoji: "🕐", command: "what time is it" },
    "date": { label: "Date", emoji: "📅", command: "what is the date" },
    "battery": { label: "Battery", emoji: "🔋", command: "battery status" },
    "status": { label: "Status", emoji: "📊", command: "system status" },
    "help": { label: "Help", emoji: "💡", command: "help" },
    
    // Applications
    "chrome": { label: "Chrome", emoji: "🌐", command: "open chrome" },
    "notepad": { label: "Notepad", emoji: "📝", command: "open notepad" },
    "files": { label: "Files", emoji: "📁", command: "open files" },
    "desktop": { label: "Desktop", emoji: "🖥️", command: "show desktop" },
    
    // System Actions
    "screenshot": { label: "Screenshot", emoji: "📸", command: "take screenshot" },
    "lock": { label: "Lock", emoji: "🔒", command: "lock computer" },
    "mute": { label: "Mute", emoji: "🔇", command: "mute" },
    
    // Volume Control
    "vol+": { label: "Vol+", emoji: "🔊", command: "volume up" },
    "vol-": { label: "Vol-", emoji: "🔉", command: "volume down" },
    
    // Timers & Reminders
    "timer5": { label: "5min Timer", emoji: "⏰", command: "set 5 minute timer" },
    "timer10": { label: "10min Timer", emoji: "⏱️", command: "set 10 minute timer" },
    "reminders": { label: "Reminders", emoji: "📋", command: "show reminders" },
    "clear": { label: "Clear All", emoji: "🗑️", command: "clear all" },
    
    // Tasks
    "morning": { label: "Morning", emoji: "🌅", command: "run morning routine" },
    "focus": { label: "Focus", emoji: "🎯", command: "focus mode" },
    "break": { label: "Break", emoji: "☕", command: "break time" },
    "tasks": { label: "Tasks", emoji: "📋", command: "list tasks" },
    "work": { label: "Work", emoji: "💼", command: "work mode" },
    "endday": { label: "End Day", emoji: "🌙", command: "end of day" },
    
    // Schedules
    "schedules": { label: "Schedules", emoji: "📅", command: "show schedules" },
};

// =====================================================
// EXECUTE COMMAND
// =====================================================

/**
 * Execute a command through the unified /command endpoint
 */
async function executeCommand(commandKey) {
    try {
        // Get command details
        const actionData = QUICK_ACTIONS[commandKey];
        if (!actionData) {
            console.error(`Unknown action: ${commandKey}`);
            return;
        }
        
        const command = actionData.command;
        console.log(`🚀 Executing: ${actionData.label} → "${command}"`);
        
        // Show loading state
        const button = document.querySelector(`[data-action="${commandKey}"]`);
        if (button) {
            button.classList.add("active");
            button.disabled = true;
        }
        
        // Send command to unified endpoint
        const response = await fetch("/command", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                command: command
            })
        });
        
        const data = await response.json();
        
        // Handle response
        if (data.success) {
            console.log(`✅ ${actionData.label}: ${data.response}`);
            displayResponse(data.response, "success", data.source);
            logActivity(`✅ ${actionData.label}: ${data.response}`, "success");
        } else {
            console.error(`❌ ${actionData.label}: ${data.response || "Unknown error"}`);
            displayResponse(`Error: ${data.response || "Action failed"}`, "error");
            logActivity(`❌ ${actionData.label} failed`, "error");
        }
        
        // Remove loading state
        if (button) {
            button.classList.remove("active");
            button.disabled = false;
        }
    
    } catch (error) {
        console.error(`❌ Command error: ${error}`);
        displayResponse(`Error: ${error.message}`, "error");
        logActivity(`❌ Error: ${error.message}`, "error");
    }
}


/**
 * Execute a custom command (for voice, text input, etc)
 */
async function executeCustomCommand(commandText) {
    try {
        console.log(`🚀 Executing custom command: "${commandText}"`);
        
        // Show loading state
        displayResponse("Processing command...", "info");
        
        // Send to command endpoint
        const response = await fetch("/command", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                command: commandText
            })
        });
        
        const data = await response.json();
        
        // Handle response
        if (data.success) {
            console.log(`✅ Command executed: ${data.response}`);
            displayResponse(data.response, "success", data.source);
            logActivity(`✅ ${data.action}: ${data.response}`, "success");
        } else {
            console.error(`❌ Command failed: ${data.response}`);
            displayResponse(`Error: ${data.response || "Command failed"}`, "error");
            logActivity(`❌ Command failed`, "error");
        }
    
    } catch (error) {
        console.error(`❌ Error: ${error}`);
        displayResponse(`Error: ${error.message}`, "error");
        logActivity(`❌ Error: ${error.message}`, "error");
    }
}


// =====================================================
// INITIALIZE BUTTONS
// =====================================================

/**
 * Initialize all quick action buttons
 */
function initializeQuickActions() {
    console.log("🎯 Initializing quick action buttons...");
    
    // Find all buttons with data-action attribute
    const buttons = document.querySelectorAll("[data-action]");
    
    buttons.forEach(button => {
        button.addEventListener("click", function(e) {
            e.preventDefault();
            const actionKey = this.getAttribute("data-action");
            executeCommand(actionKey);
        });
    });
    
    console.log(`✅ ${buttons.length} quick action buttons initialized`);
}


// =====================================================
// VOICE COMMAND HANDLER
// ===================================================

/**
 * Process voice input (from speech recognition)
 */
async function processVoiceInput(transcript) {
    console.log(`🎤 Voice input: "${transcript}"`);
    await executeCustomCommand(transcript);
}


// =====================================================
// TEXT INPUT HANDLER
// ===================================================

/**
 * Process text input from chat/input field
 */
async function processTextInput(text) {
    console.log(`⌨️ Text input: "${text}"`);
    await executeCustomCommand(text);
}


// =====================================================
// HELPER FUNCTIONS
// ===================================================

/**
 * Display response in response box
 */
function displayResponse(message, type = "info", source = "unknown") {
    const responseBox = document.getElementById("responseText") || 
                       document.querySelector(".response-text") ||
                       document.getElementById("responseBox") ||
                       document.querySelector(".ares-response");
    
    if (responseBox) {
        const className = `response-${type}`;
        const sourceText = source !== "unknown" ? ` (${source})` : "";
        responseBox.innerHTML = `
            <div class="${className}">
                ${message}
                <small style="opacity: 0.7; margin-left: 10px;">${sourceText}</small>
            </div>
        `;
    }
}


/**
 * Log activity to activity log
 */
function logActivity(message, type = "info") {
    const activityLog = document.getElementById("activityLog") || 
                       document.querySelector(".activity-log") ||
                       document.querySelector(".ares-activity");
    
    if (activityLog) {
        const entry = document.createElement("div");
        entry.className = `log-entry log-${type}`;
        
        const timestamp = new Date().toLocaleTimeString();
        entry.textContent = `[${timestamp}] ${message}`;
        
        // Add to top of log
        if (activityLog.firstChild) {
            activityLog.insertBefore(entry, activityLog.firstChild);
        } else {
            activityLog.appendChild(entry);
        }
        
        // Keep only last 30 entries
        while (activityLog.children.length > 30) {
            activityLog.removeChild(activityLog.lastChild);
        }
    }
}


/**
 * Get system status
 */
async function getSystemStatus() {
    try {
        const response = await fetch("/status");
        const status = await response.json();
        return status;
    } catch (error) {
        console.error("Status check failed:", error);
        return null;
    }
}


/**
 * Get system health
 */
async function getHealthStatus() {
    try {
        const response = await fetch("/health");
        const health = await response.json();
        return health;
    } catch (error) {
        console.error("Health check failed:", error);
        return null;
    }
}


// =====================================================
// DOM READY - INITIALIZATION
// ===================================================

document.addEventListener("DOMContentLoaded", function() {
    console.log("📄 ARES Quick Actions Module Loading...");
    
    // Initialize buttons
    initializeQuickActions();
    
    // Check system status
    getHealthStatus().then(health => {
        if (health) {
            console.log(`✅ ARES System Status: ${health.services_available}/${health.services_total} services online`);
        }
    });
    
    console.log("✅ ARES Quick Actions Ready!");
});


// =====================================================
// WINDOW CLOSE - CLEANUP
// ===================================================

window.addEventListener("beforeunload", function() {
    console.log("👋 ARES session ending...");
});