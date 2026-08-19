// ─── State ──────────────────────────────────────────────────────────
const state = {
    conversationId: null,
    currentImageFile: null,
    isTyping: false,
    mediaStream: null
};

// ─── DOM Elements ───────────────────────────────────────────────────
const feed = document.getElementById('chat-feed');
const input = document.getElementById('chat-input');
const sendBtn = document.getElementById('btn-send');
const attachBtn = document.getElementById('btn-attach');
const fileInput = document.getElementById('image-upload');
const previewBar = document.getElementById('image-preview');
const previewImg = document.getElementById('preview-img');
const removeImgBtn = document.getElementById('btn-remove-image');
const newChatBtn = document.getElementById('btn-new-chat');
const sidebarToggle = document.getElementById('btn-toggle-sidebar');
const sidebar = document.querySelector('.sidebar');
const suggestionBtns = document.querySelectorAll('.suggestion-btn');

// Camera Elements
const cameraBtn = document.getElementById('btn-camera');
const cameraModal = document.getElementById('camera-modal');
const closeCameraBtn = document.getElementById('btn-close-camera');
const cameraVideo = document.getElementById('camera-video');
const cameraCanvas = document.getElementById('camera-canvas');
const captureBtn = document.getElementById('btn-capture-photo');

// ─── Initialization ─────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
    initEventListeners();
    showWelcomeScreen();
});

function initEventListeners() {
    // Auto-resize textarea
    input.addEventListener('input', () => {
        input.style.height = 'auto';
        input.style.height = (input.scrollHeight) + 'px';
        updateSendButton();
    });

    input.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            if (!sendBtn.disabled) handleSend();
        }
    });

    sendBtn.addEventListener('click', handleSend);

    // Image Upload
    attachBtn.addEventListener('click', () => fileInput.click());
    
    fileInput.addEventListener('change', (e) => {
        handleFileSelection(e.target.files[0]);
    });

    removeImgBtn.addEventListener('click', removeImagePreview);

    // Clipboard Paste Logic
    document.addEventListener('paste', (e) => {
        const items = (e.clipboardData || e.originalEvent.clipboardData).items;
        for (let index in items) {
            const item = items[index];
            if (item.kind === 'file' && item.type.startsWith('image/')) {
                const blob = item.getAsFile();
                handleFileSelection(blob);
                e.preventDefault();
                break;
            }
        }
    });

    // Camera Logic
    cameraBtn.addEventListener('click', openCamera);
    closeCameraBtn.addEventListener('click', closeCamera);
    captureBtn.addEventListener('click', takePhoto);

    // New Chat
    newChatBtn.addEventListener('click', startNewChat);

    // Sidebar Toggle (Mobile)
    if (sidebarToggle) {
        sidebarToggle.addEventListener('click', () => {
            sidebar.classList.toggle('open');
        });
    }

    // Suggestions
    suggestionBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            const prompt = btn.getAttribute('data-prompt');
            if (sidebar.classList.contains('open')) sidebar.classList.remove('open');
            sendMessage(prompt);
        });
    });
}

function handleFileSelection(file) {
    if (file) {
        state.currentImageFile = file;
        previewImg.src = URL.createObjectURL(file);
        previewBar.classList.remove('hidden');
        updateSendButton();
    }
}

function removeImagePreview() {
    state.currentImageFile = null;
    fileInput.value = '';
    previewBar.classList.add('hidden');
    updateSendButton();
}

function updateSendButton() {
    const hasText = input.value.trim().length > 0;
    const hasImage = !!state.currentImageFile;
    sendBtn.disabled = !(hasText || hasImage) || state.isTyping;
}

// ─── Camera (WebRTC) ────────────────────────────────────────────────

async function openCamera() {
    try {
        const stream = await navigator.mediaDevices.getUserMedia({ video: { facingMode: 'user' } });
        state.mediaStream = stream;
        cameraVideo.srcObject = stream;
        cameraModal.classList.remove('hidden');
    } catch (err) {
        console.error("Camera error:", err);
        alert("Unable to access camera. Please check your browser permissions.");
    }
}

function closeCamera() {
    if (state.mediaStream) {
        state.mediaStream.getTracks().forEach(track => track.stop());
        state.mediaStream = null;
    }
    cameraModal.classList.add('hidden');
}

function takePhoto() {
    if (!state.mediaStream) return;
    
    // Set canvas dimensions to match video
    cameraCanvas.width = cameraVideo.videoWidth;
    cameraCanvas.height = cameraVideo.videoHeight;
    
    // Draw current frame
    const ctx = cameraCanvas.getContext('2d');
    ctx.drawImage(cameraVideo, 0, 0, cameraCanvas.width, cameraCanvas.height);
    
    // Convert to Blob and load into input state
    cameraCanvas.toBlob((blob) => {
        // Create a File object from the blob
        const file = new File([blob], "camera_capture.jpg", { type: "image/jpeg" });
        handleFileSelection(file);
        closeCamera();
    }, 'image/jpeg', 0.9);
}

// ─── Text-to-Speech ─────────────────────────────────────────────────

function speakText(text, btnElement) {
    if ('speechSynthesis' in window) {
        // Stop any current speech
        window.speechSynthesis.cancel();
        
        // Strip markdown formatting for speech but keep non-ASCII for Hindi/Devanagari
        const plainText = text.replace(/[*_#✦]/g, '').replace(/[✓]/g, 'check: ');
        
        const utterance = new SpeechSynthesisUtterance(plainText);
        
        // Detect if text contains Hindi/Devanagari or romanized Hindi
        const hasDevanagari = /[\u0900-\u097F]/.test(plainText);
        const voices = window.speechSynthesis.getVoices();
        
        if (hasDevanagari) {
            // Try to find a Hindi voice
            const hindiVoice = voices.find(v => v.lang.startsWith('hi'));
            if (hindiVoice) utterance.voice = hindiVoice;
        } else {
            // English or romanized — use a good English voice
            const premiumVoice = voices.find(v => v.name.includes('Google') || v.name.includes('Samantha') || v.lang === 'en-GB');
            if (premiumVoice) utterance.voice = premiumVoice;
        }

        utterance.rate = 0.95;
        utterance.pitch = 1.0;

        utterance.onstart = () => {
            if (btnElement) btnElement.classList.add('playing');
        };
        
        utterance.onend = () => {
            if (btnElement) btnElement.classList.remove('playing');
        };

        window.speechSynthesis.speak(utterance);
    } else {
        alert("Text-to-speech is not supported in your browser.");
    }
}

// Ensure voices load
window.speechSynthesis.onvoiceschanged = () => {
    window.speechSynthesis.getVoices();
};

// ─── UI Rendering ───────────────────────────────────────────────────

function showWelcomeScreen() {
    feed.innerHTML = `
        <div class="welcome-screen" id="welcome-screen">
            <h1 class="welcome-logo">Maison Hygia</h1>
            <p class="welcome-subtitle">Your personal wellness concierge. Talk to me in any language — English, Hindi, Hinglish, Marathi, or however feels natural.</p>
        </div>
    `;
}

function scrollToBottom() {
    feed.scrollTop = feed.scrollHeight;
}

function appendMessage(role, content, isHtml = false, rawTextForSpeech = null) {
    // Remove welcome screen if it exists
    const welcome = document.getElementById('welcome-screen');
    if (welcome) welcome.remove();

    const wrapper = document.createElement('div');
    wrapper.className = `message-wrapper ${role}`;
    
    const inner = document.createElement('div');
    inner.className = 'message-inner';

    const avatar = document.createElement('div');
    avatar.className = 'msg-avatar';
    avatar.textContent = role === 'ai' ? '✦' : 'U';

    const contentDiv = document.createElement('div');
    contentDiv.className = 'msg-content';
    
    if (isHtml) {
        contentDiv.innerHTML = content;
    } else {
        // Parse markdown for AI, raw text for user
        if (role === 'ai') {
            if (typeof marked !== 'undefined') {
                contentDiv.innerHTML = marked.parse(content);
            } else {
                contentDiv.textContent = content;
            }
        } else {
            contentDiv.textContent = content;
        }
    }

    inner.appendChild(avatar);
    inner.appendChild(contentDiv);
    
    // Add TTS button for AI messages
    if (role === 'ai' && (content || rawTextForSpeech)) {
        const speechBtn = document.createElement('button');
        speechBtn.className = 'speaker-btn';
        speechBtn.innerHTML = `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5"></polygon><path d="M19.07 4.93a10 10 0 0 1 0 14.14M15.54 8.46a5 5 0 0 1 0 7.07"></path></svg> Speak Output`;
        speechBtn.onclick = () => speakText(rawTextForSpeech || content, speechBtn);
        
        // Create a wrapper for content + button
        const contentContainer = document.createElement('div');
        contentContainer.style.flex = "1";
        
        inner.replaceChild(contentContainer, contentDiv);
        contentContainer.appendChild(contentDiv);
        contentContainer.appendChild(speechBtn);
    }

    wrapper.appendChild(inner);
    feed.appendChild(wrapper);
    scrollToBottom();
}

function renderRitualCard(ritual) {
    if (!ritual || !ritual.steps || ritual.steps.length === 0) return;

    const wrapper = document.createElement('div');
    wrapper.className = `message-wrapper ai`;
    
    const inner = document.createElement('div');
    inner.className = 'message-inner';

    const avatar = document.createElement('div');
    avatar.className = 'msg-avatar';
    avatar.textContent = '✦';

    const contentDiv = document.createElement('div');
    contentDiv.className = 'msg-content';

    let html = `
        <div class="ritual-card">
            <div class="ritual-header">YOUR ${ritual.moment ? ritual.moment.toUpperCase() : 'TAILORED'} RITUAL</div>
    `;

    // Extract text for speech
    let speechText = `Here is your ${ritual.moment || 'tailored'} ritual. `;

    ritual.steps.forEach((step, idx) => {
        const p = step.product;
        speechText += `Step ${idx + 1}, ${p.name}. `;
        html += `
            <div class="ritual-step">
                <div class="step-num">0${idx + 1}</div>
                <div class="step-details">
                    <h4>${p.name}</h4>
                    <p>${p.description || p.short_description || ''}</p>
                </div>
            </div>
        `;
    });

    html += `</div>`;
    contentDiv.innerHTML = html;

    const speechBtn = document.createElement('button');
    speechBtn.className = 'speaker-btn';
    speechBtn.innerHTML = `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5"></polygon><path d="M19.07 4.93a10 10 0 0 1 0 14.14M15.54 8.46a5 5 0 0 1 0 7.07"></path></svg> Speak Ritual`;
    speechBtn.onclick = () => speakText(speechText, speechBtn);

    const contentContainer = document.createElement('div');
    contentContainer.style.flex = "1";
    contentContainer.appendChild(contentDiv);
    contentContainer.appendChild(speechBtn);

    inner.appendChild(avatar);
    inner.appendChild(contentContainer);
    wrapper.appendChild(inner);
    feed.appendChild(wrapper);
    scrollToBottom();
}

function showTypingIndicator() {
    const wrapper = document.createElement('div');
    wrapper.className = `message-wrapper ai`;
    wrapper.id = 'typing-indicator';
    
    const inner = document.createElement('div');
    inner.className = 'message-inner';

    const avatar = document.createElement('div');
    avatar.className = 'msg-avatar';
    avatar.textContent = '✦';

    const contentDiv = document.createElement('div');
    contentDiv.className = 'msg-content';
    contentDiv.innerHTML = `
        <div class="typing-dots">
            <span></span><span></span><span></span>
        </div>
    `;

    inner.appendChild(avatar);
    inner.appendChild(contentDiv);
    wrapper.appendChild(inner);
    feed.appendChild(wrapper);
    scrollToBottom();
}

function hideTypingIndicator() {
    const indicator = document.getElementById('typing-indicator');
    if (indicator) indicator.remove();
}

// ─── API Interactions ───────────────────────────────────────────────

async function handleSend() {
    const text = input.value.trim();
    const file = state.currentImageFile;

    if (!text && !file) return;

    // Build user display text
    let userDisplay = text;
    if (file) {
        userDisplay += userDisplay ? '<br><i>[Attached Image]</i>' : '<i>[Attached Image]</i>';
    }

    appendMessage('user', userDisplay, true);

    // Reset input area
    input.value = '';
    input.style.height = 'auto';
    removeImagePreview();
    state.isTyping = true;
    updateSendButton();

    sendMessageToAPI(text, file);
}

async function startNewChat() {
    state.conversationId = null;
    feed.innerHTML = '';
    showWelcomeScreen();
}

async function sendMessage(text) {
    appendMessage('user', text, false);
    state.isTyping = true;
    updateSendButton();
    sendMessageToAPI(text, null);
}

async function sendMessageToAPI(text, file) {
    showTypingIndicator();

    try {
        // Ensure conversation started
        if (!state.conversationId) {
            const startRes = await fetch('/api/conversation/start', { method: 'POST' });
            if (!startRes.ok) throw new Error("Failed to start conversation");
            const startData = await startRes.json();
            state.conversationId = startData.conversation_id;
        }

        let res;
        if (file) {
            const formData = new FormData();
            formData.append('conversation_id', state.conversationId);
            formData.append('message', text || '');
            formData.append('image', file);

            res = await fetch('/api/conversation/message', {
                method: 'POST',
                body: formData
            });
        } else {
            res = await fetch('/api/conversation/message', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    conversation_id: state.conversationId,
                    message: text || ''
                })
            });
        }

        if (!res.ok) throw new Error(`API returned ${res.status}`);
        
        const data = await res.json();
        
        hideTypingIndicator();
        state.isTyping = false;
        updateSendButton();

        // Render response
        if (data.visual_observations && data.visual_observations.length > 0) {
            appendMessage('ai', `*Visual Analysis:* ${data.visual_observations.join(', ')}`);
        }

        if (data.response) {
            appendMessage('ai', data.response);
        }

        if (data.follow_up_questions && data.follow_up_questions.length > 0) {
            data.follow_up_questions.forEach(q => {
                if (q.options && q.options.length > 0) {
                    let optionsHtml = '<div class="options-container" style="display: flex; gap: 8px; flex-wrap: wrap; margin-top: 10px;">';
                    q.options.forEach(opt => {
                        // Escape single quotes in opt
                        const safeOpt = opt.replace(/'/g, "\\'");
                        optionsHtml += `<button class="option-btn" onclick="sendMessage('${safeOpt}')" style="padding: 8px 12px; border-radius: 20px; border: 1px solid var(--accent); background: transparent; color: var(--accent); cursor: pointer;">${opt}</button>`;
                    });
                    optionsHtml += '</div>';
                    appendMessage('ai', optionsHtml, true);
                }
            });
        }

        if (data.ritual) {
            renderRitualCard(data.ritual);
        }

    } catch (err) {
        console.error("Chat Error:", err);
        hideTypingIndicator();
        state.isTyping = false;
        updateSendButton();
        appendMessage('ai', "I apologize, but I am having trouble connecting to my knowledge base right now. Please try again in a moment.");
    }
}
