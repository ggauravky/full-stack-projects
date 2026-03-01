const BACKEND_URL = 'http://localhost:8000';

const chatBox = document.getElementById('chat-box');
const chatForm = document.getElementById('chat-form');
const userInput = document.getElementById('user-input');
const micBtn = document.getElementById('mic-btn');
const sendBtn = document.getElementById('send-btn');
const statusText = document.getElementById('connection-status');
const avatar = document.getElementById('status-indicator');
const recordingToast = document.getElementById('recording-toast');

let isProcessing = false;

// 1. App Initialization
window.addEventListener('DOMContentLoaded', async () => {
    try {
        const response = await fetch(`${BACKEND_URL}/health`);
        if (response.ok) {
            const data = await response.json();
            statusText.textContent = `Online - ${data.assistant}`;
            statusText.style.color = '#10b981';
            avatar.classList.add('online');
            
            setTimeout(() => {
                document.querySelector('.message.startup').remove();
                addMessage('Hello! I am JarvisLite. How can I assist you today?', 'ai');
            }, 1000);
        } else {
            throw new Error('Backend not responding properly');
        }
    } catch (error) {
        statusText.textContent = 'Backend Offline';
        statusText.style.color = '#ef4444';
        document.querySelector('.message.startup').textContent = 
            'Failed to connect to backend server. Please ensure backend is running at http://localhost:8000';
        document.querySelector('.message.startup').classList.add('error');
    }
});

// 2. Chat UI Helpers
function addMessage(text, type='ai') {
    const msgDiv = document.createElement('div');
    msgDiv.classList.add('message', type);
    // basic sanitization
    msgDiv.textContent = text;
    chatBox.appendChild(msgDiv);
    scrollToBottom();
}

function scrollToBottom() {
    chatBox.scrollTop = chatBox.scrollHeight;
}

function showTypingIndicator() {
    const indicator = document.createElement('div');
    indicator.classList.add('typing-indicator');
    indicator.id = 'typing-indicator';
    indicator.innerHTML = `
        <div class="typing-dot"></div>
        <div class="typing-dot"></div>
        <div class="typing-dot"></div>
    `;
    chatBox.appendChild(indicator);
    scrollToBottom();
}

function removeTypingIndicator() {
    const indicator = document.getElementById('typing-indicator');
    if (indicator) {
        indicator.remove();
    }
}

// 3. API Communication (Text)
chatForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    if (isProcessing) return;
    
    const text = userInput.value.trim();
    if (!text) return;
    
    // Add user message
    addMessage(text, 'user');
    userInput.value = '';
    
    await processRequest(`${BACKEND_URL}/chat`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ text })
    });
});

// 4. API Communication (Voice)
micBtn.addEventListener('click', async () => {
    if (isProcessing) return;
    
    try {
        // Update UI
        micBtn.classList.add('active');
        avatar.classList.add('listening');
        recordingToast.classList.remove('hidden');
        userInput.disabled = true;
        sendBtn.disabled = true;
        statusText.textContent = 'Listening...';
        
        await processRequest(`${BACKEND_URL}/voice`, {
            method: 'POST'
        });
        
    } finally {
        // Restore UI
        micBtn.classList.remove('active');
        avatar.classList.remove('listening');
        recordingToast.classList.add('hidden');
        userInput.disabled = false;
        sendBtn.disabled = false;
        statusText.textContent = 'Online';
        userInput.focus();
    }
});

// Generic Request Handler
async function processRequest(url, options) {
    isProcessing = true;
    showTypingIndicator();
    
    try {
        const response = await fetch(url, options);
        removeTypingIndicator();
        
        if (!response.ok) {
            throw new Error(`HTTP Error: ${response.status}`);
        }
        
        const data = await response.json();
        
        if (data.status === 'success') {
            // Pick style based on source
            const msgType = data.source === 'command' ? 'command' : 'ai';
            addMessage(data.response, msgType);
        } else {
            addMessage(data.response || data.error, 'error');
        }
        
    } catch (error) {
        removeTypingIndicator();
        console.error('Request failed:', error);
        addMessage('Failed to connect to the server. ' + error.message, 'error');
    } finally {
        isProcessing = false;
    }
}
