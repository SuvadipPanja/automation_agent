// ==========================================
// ARES MODERN UI - JARVIS STYLE
// ==========================================

// ====== GLOBAL STATE ======
let isListening = false;
let responseStartTime = 0;

// ====== DOM ELEMENTS ======
const elements = {
    commandInput: document.getElementById('commandInput'),
    responseBox: document.getElementById('responseBox'),
    coreStatus: document.getElementById('coreStatus'),
    systemStatus: document.getElementById('statusText'),
    systemTime: document.getElementById('systemTime'),
    voiceVisualizer: document.getElementById('voiceVisualizer'),
    activityLog: document.getElementById('activityLog'),
    tasksCount: document.getElementById('tasksCount'),
    schedulesCount: document.getElementById('schedulesCount'),
    responseTime: document.getElementById('responseTime'),
    loadingOverlay: document.getElementById('loadingOverlay'),
    initTime: document.getElementById('initTime')
};

// ====== INITIALIZATION ======
document.addEventListener('DOMContentLoaded', () => {
    initializeAICore();
    startSystemClock();
    loadSystemMetrics();
    setupKeyboardShortcuts();
    
    // Set initial time
    if (elements.initTime) {
        elements.initTime.textContent = getCurrentTime();
    }
    
    logActivity('ARES interface loaded successfully');
});

// ====== SYSTEM CLOCK ======
function startSystemClock() {
    updateClock();
    setInterval(updateClock, 1000);
}

function updateClock() {
    if (elements.systemTime) {
        elements.systemTime.textContent = getCurrentTime();
    }
}

function getCurrentTime() {
    const now = new Date();
    return now.toLocaleTimeString('en-US', { hour12: false });
}

// ====== AI CORE VISUALIZATION ======
function initializeAICore() {
    const canvas = document.getElementById('aiCoreCanvas');
    if (!canvas) return;
    
    const ctx = canvas.getContext('2d');
    canvas.width = canvas.offsetWidth;
    canvas.height = canvas.offsetHeight;
    
    // Particle system
    const particles = [];
    const particleCount = 50; // Reduced from 100 for better performance
    const centerX = canvas.width / 2;
    const centerY = canvas.height / 2;
    
    class Particle {
        constructor() {
            this.angle = Math.random() * Math.PI * 2;
            this.radius = Math.random() * 100 + 50;
            this.speed = Math.random() * 0.005 + 0.002;
            this.size = Math.random() * 2 + 1;
            this.opacity = Math.random() * 0.5 + 0.3;
        }
        
        update() {
            this.angle += this.speed;
            if (this.angle > Math.PI * 2) this.angle = 0;
        }
        
        draw() {
            const x = centerX + Math.cos(this.angle) * this.radius;
            const y = centerY + Math.sin(this.angle) * this.radius;
            
            ctx.beginPath();
            ctx.arc(x, y, this.size, 0, Math.PI * 2);
            ctx.fillStyle = `rgba(0, 217, 255, ${this.opacity})`;
            ctx.fill();
            
            // Connection lines to center
            ctx.beginPath();
            ctx.moveTo(centerX, centerY);
            ctx.lineTo(x, y);
            ctx.strokeStyle = `rgba(0, 217, 255, ${this.opacity * 0.1})`;
            ctx.lineWidth = 0.5;
            ctx.stroke();
        }
    }
    
    // Initialize particles
    for (let i = 0; i < particleCount; i++) {
        particles.push(new Particle());
    }
    
    // Center core
    function drawCore() {
        // Outer ring
        ctx.beginPath();
        ctx.arc(centerX, centerY, 60, 0, Math.PI * 2);
        ctx.strokeStyle = 'rgba(0, 217, 255, 0.3)';
        ctx.lineWidth = 2;
        ctx.stroke();
        
        // Inner glow
        const gradient = ctx.createRadialGradient(centerX, centerY, 0, centerX, centerY, 40);
        gradient.addColorStop(0, 'rgba(0, 217, 255, 0.4)');
        gradient.addColorStop(1, 'rgba(0, 217, 255, 0)');
        ctx.fillStyle = gradient;
        ctx.beginPath();
        ctx.arc(centerX, centerY, 40, 0, Math.PI * 2);
        ctx.fill();
        
        // Center dot
        ctx.beginPath();
        ctx.arc(centerX, centerY, 8, 0, Math.PI * 2);
        ctx.fillStyle = '#00d9ff';
        ctx.fill();
        ctx.shadowBlur = 20;
        ctx.shadowColor = '#00d9ff';
    }
    
    // Animation loop
    function animate() {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        
        drawCore();
        
        particles.forEach(particle => {
            particle.update();
            particle.draw();
        });
        
        requestAnimationFrame(animate);
    }
    
    animate();
}

// ====== STATUS MANAGEMENT ======
function setStatus(status) {
    const statusMap = {
        'IDLE': { text: 'IDLE', color: 'var(--text-secondary)' },
        'LISTENING': { text: 'LISTENING', color: 'var(--warning-color)' },
        'THINKING': { text: 'PROCESSING', color: 'var(--primary-color)' },
        'RESPONDING': { text: 'RESPONDING', color: 'var(--success-color)' },
        'ERROR': { text: 'ERROR', color: 'var(--error-color)' }
    };
    
    const statusInfo = statusMap[status] || statusMap['IDLE'];
    
    if (elements.coreStatus) {
        elements.coreStatus.textContent = statusInfo.text;
        elements.coreStatus.style.color = statusInfo.color;
    }
    
    if (elements.systemStatus) {
        elements.systemStatus.textContent = statusInfo.text;
    }
}

// ====== LOADING OVERLAY ======
function showLoading() {
    if (elements.loadingOverlay) {
        elements.loadingOverlay.classList.add('active');
    }
}

function hideLoading() {
    if (elements.loadingOverlay) {
        elements.loadingOverlay.classList.remove('active');
    }
}

// ====== ACTIVITY LOGGING ======
function logActivity(message, type = 'info') {
    if (!elements.activityLog) return;
    
    const entry = document.createElement('div');
    entry.className = 'log-entry';
    
    const time = document.createElement('span');
    time.className = 'log-time';
    time.textContent = getCurrentTime();
    
    const text = document.createElement('span');
    text.className = `log-text text-${type}`;
    text.textContent = message;
    
    entry.appendChild(time);
    entry.appendChild(text);
    
    elements.activityLog.insertBefore(entry, elements.activityLog.firstChild);
    
    // Keep only last 10 entries
    while (elements.activityLog.children.length > 10) {
        elements.activityLog.removeChild(elements.activityLog.lastChild);
    }
}

// ====== VOICE VISUALIZER ======
function activateVoiceVisualizer() {
    if (elements.voiceVisualizer) {
        elements.voiceVisualizer.classList.add('active');
    }
}

function deactivateVoiceVisualizer() {
    if (elements.voiceVisualizer) {
        elements.voiceVisualizer.classList.remove('active');
    }
}

// ====== TEXT TO SPEECH ======
function speak(text) {
    if (!text || !('speechSynthesis' in window)) return;
    
    window.speechSynthesis.cancel();
    
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.rate = 0.95;
    utterance.pitch = 1.0;
    utterance.volume = 1.0;
    utterance.lang = 'en-US';
    
    utterance.onstart = () => {
        setStatus('RESPONDING');
    };
    
    utterance.onend = () => {
        setStatus('IDLE');
    };
    
    window.speechSynthesis.speak(utterance);
}

// ====== COMMAND SENDING ======
async function sendCommand(textOverride = null) {
    const cmd = textOverride || elements.commandInput.value.trim();
    if (!cmd) return;
    
    setStatus('THINKING');
    // Removed showLoading() - it blocks the UI
    responseStartTime = Date.now();
    
    // Display user input
    displayResponse(`> ${cmd}\n\nProcessing...`, 'user-input');
    
    logActivity(`Command: ${cmd}`, 'primary');
    
    try {
        const response = await fetch('/ai-command', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ command: cmd })
        });
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }
        
        const data = await response.json();
        
        // Calculate response time
        const responseTime = Date.now() - responseStartTime;
        updateResponseTime(responseTime);
        
        // Handle response
        let displayText = '';
        let speechText = '';
        
        if (data.reply) {
            displayText = data.reply;
            speechText = data.reply;
        } else if (data.response) {
            displayText = typeof data.response === 'string' 
                ? data.response 
                : JSON.stringify(data.response, null, 2);
            speechText = data.speech || 'Command processed';
        } else {
            displayText = JSON.stringify(data, null, 2);
            speechText = 'Response received';
        }
        
        displayResponse(displayText, 'assistant');
        speak(speechText);
        
        logActivity('Response received', 'success');
        
    } catch (error) {
        displayResponse(`❌ Error: ${error.message}`, 'error');
        logActivity(`Error: ${error.message}`, 'error');
        setStatus('ERROR');
        setTimeout(() => setStatus('IDLE'), 3000);
    } finally {
        elements.commandInput.value = '';
        setStatus('IDLE');
    }
}

// ====== VOICE INPUT ======
function sendVoice() {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    
    if (!SpeechRecognition) {
        displayResponse('❌ Speech recognition not supported in this browser', 'error');
        logActivity('Speech recognition not supported', 'error');
        return;
    }
    
    const recognition = new SpeechRecognition();
    recognition.lang = 'en-US';
    recognition.interimResults = false;
    recognition.maxAlternatives = 1;
    
    const voiceBtn = document.querySelector('.btn-voice');
    
    recognition.onstart = () => {
        isListening = true;
        setStatus('LISTENING');
        activateVoiceVisualizer();
        voiceBtn.classList.add('active');
        displayResponse('🎙 Listening...', 'info');
        logActivity('Voice input started', 'warning');
    };
    
    recognition.onresult = (event) => {
        const transcript = event.results[0][0].transcript;
        displayResponse(`🎙 Heard: "${transcript}"`, 'success');
        logActivity(`Voice: ${transcript}`, 'primary');
        sendCommand(transcript);
    };
    
    recognition.onerror = (event) => {
        displayResponse(`❌ Voice error: ${event.error}`, 'error');
        logActivity(`Voice error: ${event.error}`, 'error');
    };
    
    recognition.onend = () => {
        isListening = false;
        deactivateVoiceVisualizer();
        voiceBtn.classList.remove('active');
        setStatus('IDLE');
    };
    
    recognition.start();
}

// ====== RESPONSE DISPLAY ======
function displayResponse(text, type = 'normal') {
    if (!elements.responseBox) return;
    
    const typeStyles = {
        'user-input': 'color: var(--accent-color);',
        'assistant': 'color: var(--text-primary);',
        'error': 'color: var(--error-color);',
        'success': 'color: var(--success-color);',
        'info': 'color: var(--warning-color);',
        'normal': 'color: var(--text-primary);'
    };
    
    const style = typeStyles[type] || typeStyles.normal;
    
    elements.responseBox.innerHTML = `<div style="${style}">${text.replace(/\n/g, '<br>')}</div>`;
    elements.responseBox.scrollTop = elements.responseBox.scrollHeight;
}

function clearResponse() {
    if (elements.responseBox) {
        elements.responseBox.innerHTML = `
            <div class="welcome-message">
                <p>⚡ <strong>ARES INITIALIZED</strong></p>
                <p>All systems operational. Ready to assist.</p>
                <p class="hint">💡 Try saying: "Hello", "What can you do?", or "Help"</p>
            </div>
        `;
    }
    logActivity('Response cleared', 'info');
}

// ====== QUICK ACTIONS ======
async function quickAction(action) {
    logActivity(`Quick action: ${action}`, 'primary');
    
    const actions = {
        'health': checkHealth,
        'tasks': loadTasks,
        'schedules': loadSchedules,
        'reload': reloadSchedules
    };
    
    const actionFn = actions[action];
    if (actionFn) {
        await actionFn();
    }
}

async function checkHealth() {
    setStatus('THINKING');
    
    try {
        const response = await fetch('/health');
        const data = await response.json();
        
        displayResponse(
            `✅ System Health Check\n\n` +
            `Agent: ${data.agent}\n` +
            `Status: ${data.status}\n` +
            `Time: ${data.time}`,
            'success'
        );
        
        speak('System is online and operational');
        logActivity('Health check completed', 'success');
        
    } catch (error) {
        displayResponse(`❌ Health check failed: ${error.message}`, 'error');
        logActivity('Health check failed', 'error');
    } finally {
        setStatus('IDLE');
    }
}

async function loadTasks() {
    setStatus('THINKING');
    
    try {
        const response = await fetch('/tasks');
        const tasks = await response.json();
        
        if (Array.isArray(tasks)) {
            const taskList = tasks.map(t => `  • ${t.name || t}`).join('\n');
            displayResponse(`⚡ Available Tasks\n\n${taskList}`, 'info');
            
            if (elements.tasksCount) {
                elements.tasksCount.textContent = tasks.length;
            }
        } else {
            displayResponse(JSON.stringify(tasks, null, 2), 'normal');
        }
        
        speak(`${tasks.length} tasks loaded`);
        logActivity(`Loaded ${tasks.length} tasks`, 'success');
        
    } catch (error) {
        displayResponse(`❌ Failed to load tasks: ${error.message}`, 'error');
        logActivity('Task loading failed', 'error');
    } finally {
        setStatus('IDLE');
    }
}

async function loadSchedules() {
    setStatus('THINKING');
    
    try {
        const response = await fetch('/schedules');
        const schedules = await response.json();
        
        if (Array.isArray(schedules)) {
            const scheduleList = schedules.map(s => 
                `  • ${s.task} - ${s.time} (${s.type}) ${s.enabled ? '✓' : '✗'}`
            ).join('\n');
            
            displayResponse(`⏰ Active Schedules\n\n${scheduleList}`, 'info');
            
            if (elements.schedulesCount) {
                const activeCount = schedules.filter(s => s.enabled).length;
                elements.schedulesCount.textContent = activeCount;
            }
        } else {
            displayResponse(JSON.stringify(schedules, null, 2), 'normal');
        }
        
        speak('Schedules loaded');
        logActivity(`Loaded ${schedules.length} schedules`, 'success');
        
    } catch (error) {
        displayResponse(`❌ Failed to load schedules: ${error.message}`, 'error');
        logActivity('Schedule loading failed', 'error');
    } finally {
        setStatus('IDLE');
    }
}

async function reloadSchedules() {
    setStatus('THINKING');
    
    try {
        const response = await fetch('/reload-schedules', { method: 'POST' });
        const data = await response.json();
        
        displayResponse('✅ Schedules reloaded successfully', 'success');
        speak('Schedules reloaded');
        logActivity('Schedules reloaded', 'success');
        
    } catch (error) {
        displayResponse(`❌ Reload failed: ${error.message}`, 'error');
        logActivity('Reload failed', 'error');
    } finally {
        setStatus('IDLE');
    }
}

// ====== SYSTEM METRICS ======
async function loadSystemMetrics() {
    // Load initial metrics
    await loadTasks();
    await loadSchedules();
}

function updateResponseTime(ms) {
    if (elements.responseTime) {
        elements.responseTime.textContent = `${ms}ms`;
    }
}

// ====== KEYBOARD SHORTCUTS ======
function setupKeyboardShortcuts() {
    if (elements.commandInput) {
        elements.commandInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                sendCommand();
            }
        });
    }
    
    // Global shortcuts
    document.addEventListener('keydown', (e) => {
        // Ctrl/Cmd + K - Focus input
        if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
            e.preventDefault();
            elements.commandInput.focus();
        }
        
        // Ctrl/Cmd + L - Clear response
        if ((e.ctrlKey || e.metaKey) && e.key === 'l') {
            e.preventDefault();
            clearResponse();
        }
        
        // Ctrl/Cmd + Space - Voice input
        if ((e.ctrlKey || e.metaKey) && e.key === ' ') {
            e.preventDefault();
            sendVoice();
        }
    });
}

// ====== EXPOSE TO WINDOW ======
window.sendCommand = sendCommand;
window.sendVoice = sendVoice;
window.quickAction = quickAction;
window.clearResponse = clearResponse;
window.checkHealth = checkHealth;
window.loadTasks = loadTasks;
window.loadSchedules = loadSchedules;
window.reloadSchedules = reloadSchedules;
window.setStatus = setStatus;
window.logActivity = logActivity;
window.addActivityLog = logActivity;  // Alias for voice.js compatibility

console.log('🚀 ARES Modern UI Initialized');
console.log('Keyboard shortcuts:');
console.log('  - Ctrl/Cmd + K: Focus input');
console.log('  - Ctrl/Cmd + L: Clear response');
console.log('  - Ctrl/Cmd + Space: Voice input');