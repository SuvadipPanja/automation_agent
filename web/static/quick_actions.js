/**
 * =====================================================
 * ARES QUICK ACTION BUTTONS
 * =====================================================
 * Handles all quick action buttons:
 * - Direct automation (no AI processing)
 * - Real-time execution
 * - Immediate response
 * - Task, reminder, schedule management
 * =====================================================
 */

// =====================================================
// QUICK ACTION DEFINITIONS
// =====================================================
const QUICK_ACTIONS = {
    // System & Info
    "time": { label: "Time", emoji: "🕐", action: "time" },
    "date": { label: "Date", emoji: "📅", action: "date" },
    "battery": { label: "Battery", emoji: "🔋", action: "battery" },
    "status": { label: "Status", emoji: "📊", action: "status" },
    "help": { label: "Help", emoji: "💡", action: "help" },
    
    // Applications
    "chrome": { label: "Chrome", emoji: "🌐", action: "chrome" },
    "notepad": { label: "Notepad", emoji: "📝", action: "notepad" },
    "files": { label: "Files", emoji: "📁", action: "files" },
    "desktop": { label: "Desktop", emoji: "🖥️", action: "desktop" },
    
    // System Actions
    "screenshot": { label: "Screenshot", emoji: "📸", action: "screenshot" },
    "lock": { label: "Lock", emoji: "🔒", action: "lock" },
    "mute": { label: "Mute", emoji: "🔇", action: "mute" },
    
    // Volume Control
    "vol+": { label: "Vol+", emoji: "🔊", action: "vol+" },
    "vol-": { label: "Vol-", emoji: "🔉", action: "vol-" },
    
    // Timers & Reminders
    "timer5": { label: "5min Timer", emoji: "⏰", action: "5min timer" },
    "timer10": { label: "10min Timer", emoji: "⏱️", action: "10min timer" },
    "reminders": { label: "Reminders", emoji: "📋", action: "reminders" },
    "clear": { label: "Clear All", emoji: "🗑️", action: "clear all" },
    
    // Tasks
    "morning": { label: "Morning", emoji: "🌅", action: "morning" },
    "focus": { label: "Focus", emoji: "🎯", action: "focus" },
    "break": { label: "Break", emoji: "☕", action: "break" },
    "tasks": { label: "Tasks", emoji: "📋", action: "tasks" },
    "work": { label: "Work", emoji: "💼", action: "work" },
    "endday": { label: "End Day", emoji: "🌙", action: "end day" },
    
    // Schedules
    "schedules": { label: "Schedules", emoji: "📅", action: "schedules" },
};

// =====================================================
// EXECUTE QUICK ACTION
// =====================================================
async function executeQuickAction(actionKey) {
    try {
        // Get action details
        const action = QUICK_ACTIONS[actionKey];
        if (!action) {
            console.error(`Unknown action: ${actionKey}`);
            return;
        }
        
        console.log(`🚀 Executing quick action: ${action.label}`);
        
        // Show loading state
        const button = document.querySelector(`[data-action="${actionKey}"]`);
        if (button) {
            button.classList.add("active");
            button.disabled = true;
        }
        
        // Send to direct-action endpoint
        const response = await fetch("/direct-action", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                action: action.action
            })
        });
        
        const data = await response.json();
        
        // Display response
        if (data.success) {
            console.log(`✅ ${action.label}: ${data.response}`);
            displayResponse(data.response, "success");
            logActivity(`✅ ${action.label}: ${data.response}`, "success");
        } else {
            console.error(`❌ ${action.label} failed: ${data.error || "Unknown error"}`);
            displayResponse(`Error: ${data.error || "Action failed"}`, "error");
            logActivity(`❌ ${action.label} failed`, "error");
        }
        
        // Remove loading state
        if (button) {
            button.classList.remove("active");
            button.disabled = false;
        }
    
    } catch (error) {
        console.error(`❌ Quick action error: ${error}`);
        displayResponse(`Error: ${error.message}`, "error");
        logActivity(`❌ Error: ${error.message}`, "error");
    }
}

// =====================================================
// INITIALIZE QUICK ACTION BUTTONS
// =====================================================
function initializeQuickActions() {
    console.log("🎯 Initializing quick action buttons...");
    
    // Find all quick action buttons
    const buttons = document.querySelectorAll("[data-action]");
    
    buttons.forEach(button => {
        button.addEventListener("click", function(e) {
            e.preventDefault();
            const actionKey = this.getAttribute("data-action");
            executeQuickAction(actionKey);
        });
    });
    
    console.log(`✅ ${buttons.length} quick action buttons initialized`);
}

// =====================================================
// HELPER FUNCTIONS
// =====================================================

/**
 * Display response in the response box
 */
function displayResponse(message, type = "info") {
    const responseBox = document.getElementById("responseText") || 
                       document.querySelector(".response-text") ||
                       document.getElementById("responseBox");
    
    if (responseBox) {
        responseBox.innerHTML = `<div class="response-${type}">${message}</div>`;
    }
}

/**
 * Log activity to activity log
 */
function logActivity(message, type = "info") {
    const activityLog = document.getElementById("activityLog") || 
                       document.querySelector(".activity-log");
    
    if (activityLog) {
        const entry = document.createElement("div");
        entry.className = `log-entry log-${type}`;
        entry.textContent = `[${new Date().toLocaleTimeString()}] ${message}`;
        
        // Add to top of log
        if (activityLog.firstChild) {
            activityLog.insertBefore(entry, activityLog.firstChild);
        } else {
            activityLog.appendChild(entry);
        }
        
        // Keep only last 20 entries
        while (activityLog.children.length > 20) {
            activityLog.removeChild(activityLog.lastChild);
        }
    }
}

// =====================================================
// DOM READY
// ===================================================
document.addEventListener("DOMContentLoaded", function() {
    console.log("📄 Quick Actions Module Loading...");
    initializeQuickActions();
    console.log("✅ Quick Actions Ready!");
});