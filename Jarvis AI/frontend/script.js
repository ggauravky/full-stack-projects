const BACKEND_URL = 'http://localhost:8000';

const chatBox = document.getElementById('chat-box');
const chatForm = document.getElementById('chat-form');
const userInput = document.getElementById('user-input');
const micBtn = document.getElementById('mic-btn');
const sendBtn = document.getElementById('send-btn');
const statusText = document.getElementById('connection-status');
const avatar = document.getElementById('status-indicator');
const recordingToast = document.getElementById('recording-toast');

// Image upload elements
const uploadBtn = document.getElementById('upload-btn');
const imageUpload = document.getElementById('image-upload');
const imagePreviewContainer = document.getElementById('image-preview-container');
const imagePreview = document.getElementById('image-preview');
const clearImageBtn = document.getElementById('clear-image-btn');

let isProcessing = false;
let selectedImageFile = null;

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

// SSE Events Connection
const eventSource = new EventSource(`${BACKEND_URL}/events`);

eventSource.onmessage = function (event) {
    try {
        const data = JSON.parse(event.data);
        removeTypingIndicator(); // Ensure UI unfreezes when server broadcasts the final result

        if (data.status === 'success') {
            const msgType = data.source === 'command' ? 'command' : 'ai';
            addMessage(data.response, msgType);
        } else {
            addMessage(data.response || data.error, 'error');
        }

        isProcessing = false;

        // Restore voice UI if it was locked
        micBtn.classList.remove('active');
        avatar.classList.remove('listening');
        recordingToast.classList.add('hidden');
        userInput.disabled = false;
        sendBtn.disabled = false;
        statusText.textContent = 'Online';

    } catch (e) {
        console.error("Error parsing SSE msg", e);
    }
};

eventSource.onerror = function (error) {
    console.error("SSE connection lost or error", error);
};

// 2. Chat UI Helpers
function addMessage(text, type = 'ai', imageUrl = null) {
    const msgDiv = document.createElement('div');
    msgDiv.classList.add('message', type);

    let contentHtml = '';

    // If there's an image attached to the message (for User messages)
    if (imageUrl) {
        contentHtml += `<img src="${imageUrl}" class="chat-image" alt="Uploaded Image"><br>`;
    }

    // Use marked for parsed markdown styling if it's the AI response
    if (type === 'ai' || type === 'command') {
        contentHtml += marked.parse(text);
    } else {
        contentHtml += text; // user text is raw
    }

    msgDiv.innerHTML = contentHtml;

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
        <div class="wave-bar"></div>
        <div class="wave-bar"></div>
        <div class="wave-bar"></div>
        <div class="wave-bar"></div>
        <div class="wave-bar"></div>
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

// 3. Image Upload Handlers
uploadBtn.addEventListener('click', () => {
    imageUpload.click();
});

imageUpload.addEventListener('change', (e) => {
    const file = e.target.files[0];
    if (file) {
        selectedImageFile = file;
        const reader = new FileReader();
        reader.onload = function (e) {
            imagePreview.src = e.target.result;
            imagePreviewContainer.classList.remove('image-preview-hidden');
            userInput.focus();
        }
        reader.readAsDataURL(file);
    }
});

clearImageBtn.addEventListener('click', clearImageSelection);

function clearImageSelection() {
    selectedImageFile = null;
    imageUpload.value = '';
    imagePreview.src = '';
    imagePreviewContainer.classList.add('image-preview-hidden');
}

// 4. API Communication (Text & Vision)
chatForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    if (isProcessing) return;

    const text = userInput.value.trim();
    if (!text && !selectedImageFile) return;

    // Save image ref for UI before clearing
    const imagePreviewUrl = imagePreview.src;
    const hasImage = !!selectedImageFile;
    const currentFile = selectedImageFile; // keep standard reference before reset

    // Add user message to UI
    if (hasImage) {
        addMessage(text || "Uploaded an image.", 'user', imagePreviewUrl);
    } else {
        addMessage(text, 'user');
    }

    // Clear Input UI
    userInput.value = '';
    clearImageSelection();

    // Prepare Request based on Vision vs Text
    if (hasImage) {
        const formData = new FormData();
        formData.append('image', currentFile);
        if (text) formData.append('text', text);

        await processRequest(`${BACKEND_URL}/vision`, {
            method: 'POST',
            body: formData  // Fetch automatically sets multipart/form-data with bounds for FormData
        });
    } else {
        await processRequest(`${BACKEND_URL}/chat`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ text })
        });
    }
});

// 5. API Communication (Voice)
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

// Generic Request Handler (Updated for Async mode)
async function processRequest(url, options) {
    isProcessing = true;
    showTypingIndicator(); // Shows permanently until SSE returns

    try {
        const response = await fetch(url, options);

        if (!response.ok) {
            removeTypingIndicator();
            isProcessing = false;
            throw new Error(`HTTP Error: ${response.status}`);
        }

        const data = await response.json();

        // Handling voice edge cases (where whisper fails fast)
        if (data.status === 'error' && data.message) {
            removeTypingIndicator();
            addMessage(data.message, 'error');
            isProcessing = false;

            // Restore Voice UI
            micBtn.classList.remove('active');
            avatar.classList.remove('listening');
            recordingToast.classList.add('hidden');
            userInput.disabled = false;
            sendBtn.disabled = false;
            statusText.textContent = 'Online';
        }
        // If accepted, we just wait for SSE push. 
        // DO NOT unlock 'isProcessing' until SSE pushes the final payload onmessage.

    } catch (error) {
        removeTypingIndicator();
        isProcessing = false;
        console.error('Request failed:', error);
        addMessage('Failed to connect to the server. ' + error.message, 'error');
    }
}
