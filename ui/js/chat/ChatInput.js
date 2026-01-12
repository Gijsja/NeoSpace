/**
 * ChatInput.js
 * Handles message input, typing events, and file uploads.
 */
import { state } from './ChatState.js';
import { sendMessage, sendTyping } from './ChatSocket.js';
import { showToast } from './ChatUI.js';


export function setupChatInput() {
    const messageForm = document.getElementById('message-form');
    const messageInput = document.getElementById('input');
    const sendBtn = document.getElementById('send-btn');
    const uploadBtn = document.getElementById('upload-btn');
    const fileInput = document.getElementById('file-input');
    const dragOverlay = document.getElementById('drag-overlay');
    const emojiBtn = document.getElementById('emoji-btn');
    const emojiPickerContainer = document.getElementById('emoji-picker-container');
    const emojiPicker = document.querySelector('emoji-picker');

    // 1. Send Message
    if (messageForm) {
        messageForm.addEventListener('submit', (e) => {
            e.preventDefault();
            const content = messageInput.value.trim();
            if (!content || state.isLoading) return;

            setLoading(true);
            try {
                sendMessage(content);
                window.dispatchEvent(new CustomEvent('message-sent'));
                messageInput.value = '';
                // Stop typing immediately
                clearTimeout(state.typingTimeout);
                state.isTyping = false;
                sendTyping(false);
            } catch (err) {
                showToast('Failed to send', 'error');
            } finally {
                setLoading(false);
                messageInput.focus();
            }
        });
    }

    // 2. Typing Indicator
    if (messageInput) {
        messageInput.addEventListener('input', () => {
            if (!state.isTyping) {
                state.isTyping = true;
                sendTyping(true);
            }
            clearTimeout(state.typingTimeout);
            state.typingTimeout = setTimeout(() => {
                state.isTyping = false;
                sendTyping(false);
            }, 2000);
        });
    }

    // 3. Emoji Picker
    if (emojiBtn && emojiPickerContainer && emojiPicker) {
        emojiBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            emojiPickerContainer.classList.toggle('hidden');
        });
        emojiPicker.addEventListener('emoji-click', (event) => {
            insertAtCursor(messageInput, event.detail.unicode);
            emojiPickerContainer.classList.add('hidden');
        });
        document.addEventListener('click', (e) => {
            if (!emojiPickerContainer.contains(e.target) && e.target !== emojiBtn && !emojiBtn.contains(e.target)) {
                emojiPickerContainer.classList.add('hidden');
            }
        });
        emojiPickerContainer.addEventListener('click', (e) => e.stopPropagation());
    }

    // 4. File Upload (Click)
    if (uploadBtn && fileInput) {
        uploadBtn.addEventListener('click', () => fileInput.click());
        fileInput.addEventListener('change', () => {
            if (fileInput.files.length > 0) {
                handleUpload(fileInput.files[0]);
                fileInput.value = '';
            }
        });
    }

    // 5. Drag & Drop
    const dropZone = document.body;
    if (dragOverlay) {
        ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
            dropZone.addEventListener(eventName, (e) => { e.preventDefault(); e.stopPropagation(); }, false);
        });
        dropZone.addEventListener('dragenter', () => dragOverlay.classList.remove('hidden'));
        dragOverlay.addEventListener('dragleave', (e) => {
            if (e.clientX <= 0 || e.clientY <= 0 || e.clientX >= window.innerWidth || e.clientY >= window.innerHeight) {
                dragOverlay.classList.add('hidden');
            }
        });
        dropZone.addEventListener('drop', (e) => {
            dragOverlay.classList.add('hidden');
            if (e.dataTransfer.files.length > 0) handleUpload(e.dataTransfer.files[0]);
        });
    }

    // 6. Voice Recorder
    const recordBtn = document.getElementById('record-btn');
    const overlay = document.getElementById('recording-overlay');
    const stopBtn = document.getElementById('stop-recording');
    const cancelBtn = document.getElementById('cancel-recording');

    if (recordBtn && overlay && window.VoiceRecorder) {
        const recorder = new window.VoiceRecorder('voice-canvas');

        recordBtn.addEventListener('click', async () => {
            try {
                await recorder.start();
                overlay.classList.remove('hidden');
            } catch (e) {
                showToast('Microphone access denied', 'error');
            }
        });

        stopBtn.addEventListener('click', async () => {
            const result = await recorder.stop();
            overlay.classList.add('hidden');

            if (result && result.blob) {
                // Upload Blob
                uploadVoice(result.blob, result.waveform);
            }
        });

        cancelBtn.addEventListener('click', async () => {
            await recorder.stop(); // Just stop, ignore result
            overlay.classList.add('hidden');
        });
    }
}

async function uploadVoice(blob, waveform) {
    setLoading(true);
    const formData = new FormData();
    // Rename blob to .webm for backend detection
    formData.append('file', blob, 'voice_message.webm');

    try {
        const res = await fetch('/upload', {
            method: 'POST',
            body: formData
        });
        const data = await res.json();

        if (res.ok) {
            // Encode waveform data to send with message
            // format: audio:URL|waveform_data
            // Waveform data is array [0.1, 0.5, ...]. Join with commas.
            // But comma might break parsing? Base64?
            // Simplest: just send audio:URL for now, and let client compute waveform? 
            // Or use JSON string: audio:{"url":"...", "wave":[...]}
            // ChatSocket.js expects string?
            // Existing format: `img:URL`.
            // Let's use `audio:URL` for now. Visualizer can compute locally or just show simple bar.
            // Better: `audio:URL`
            sendMessage(`audio:${data.url}`);
        } else {
            showToast(data.error || 'Upload failed', 'error');
        }
    } catch (e) {
        showToast('Upload error', 'error');
    } finally {
        setLoading(false);
    }
}

function setLoading(loading) {
    state.isLoading = loading;
    const sendBtn = document.getElementById('send-btn');
    if (sendBtn) {
        sendBtn.disabled = loading;
        sendBtn.textContent = loading ? '...' : 'Send';
    }
}

function insertAtCursor(input, text) {
    if (!input) return;
    const start = input.selectionStart;
    const end = input.selectionEnd;
    const value = input.value;
    input.value = value.substring(0, start) + text + value.substring(end);
    input.selectionStart = input.selectionEnd = start + text.length;
    input.focus();
}

async function handleUpload(file) {
    if (!file.type.startsWith('image/')) {
        showToast('Only images supported', 'warning');
        return;
    }
    setLoading(true);
    const formData = new FormData();
    formData.append('file', file);
    try {
        const res = await fetch('/upload', {
            method: 'POST',
            body: formData,
            headers: { 'X-User': state.currentUser || 'anonymous' }
        });
        const data = await res.json();
        if (res.ok) {
            sendMessage(`img:${data.url}`);
        } else {
            showToast(data.error || 'Upload failed', 'error');
        }
    } catch (err) {
        showToast('Upload error', 'error');
    } finally {
        setLoading(false);
    }
}
