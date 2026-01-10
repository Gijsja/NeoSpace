/**
 * WallEdit.js
 * Handles the Edit Profile modal and logic.
 */

import { state } from './WallState.js';

const editModal = document.getElementById('edit-modal');
const editForm = document.getElementById('edit-form');
let voiceBlob = null;
let voiceWaveform = null;

export function setupEditForm(callbacks) {
    if (!editForm) return;

    // Close buttons
    document.querySelectorAll('.close-modal').forEach(b => {
        b.onclick = () => {
            window.dispatchEvent(new CustomEvent('close-edit-modal'));
            if (state.voiceRecorder) state.voiceRecorder.stop();
        };
    });

    // Voice Recorder Logic
    setupVoiceRecorder(callbacks.onRender);

    // Avatar Upload
    setupAvatarUpload(callbacks.onRender);

    // Form Submit
    editForm.onsubmit = async (e) => {
        e.preventDefault();
        const formData = new FormData(editForm);
        const payload = Object.fromEntries(formData.entries());

        // Checkboxes
        payload.is_public = formData.get('is_public') === 'on';
        payload.show_online_status = formData.get('show_online_status') === 'on';
        payload.anthem_autoplay = formData.get('anthem_autoplay') === 'on';

        // Add dm_policy if not present
        if (!payload.dm_policy) {
            payload.dm_policy = state.currentUserData?.dm_policy || 'everyone';
        }

        try {
            const csrfToken = document.querySelector('meta[name="csrf-token"]')?.getAttribute('content');

            const res = await fetch('/profile/update', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRF-TOKEN': csrfToken || ''
                },
                body: JSON.stringify(payload)
            });
            const data = await res.json();
            if (data.ok) {
                window.dispatchEvent(new CustomEvent('close-edit-modal'));
                if (callbacks.onSuccess) callbacks.onSuccess();
            } else {
                alert(data.error || "Update failed");
            }
        } catch (err) {
            alert("Update error");
        }
    };
}

export function openEditModal() {
    if (!state.currentUserData) return;
    const d = state.currentUserData;

    // Fill main fields
    setVal('input-name', d.display_name);
    setVal('input-bio', d.bio);
    setVal('input-status-msg', d.status_message);
    setVal('input-status-emoji', d.status_emoji || "👋");
    setVal('input-now-activity', d.now_activity);
    setVal('input-now-type', d.now_activity_type || "thinking");
    setVal('input-theme', d.theme_preset);
    setVal('input-accent', d.accent_color);
    setVal('input-anthem-url', d.anthem_url);

    // Checkboxes
    setCheck('input-public', d.is_public !== false);
    setCheck('input-online', d.show_online_status !== false);
    setCheck('input-anthem-autoplay', d.anthem_autoplay !== false);

    // Avatar Preview
    const prev = document.getElementById('preview-avatar');
    if (prev) {
        if (d.avatar_path) prev.style.backgroundImage = `url('${d.avatar_path}')`;
        else {
            prev.style.backgroundImage = '';
            prev.textContent = d.display_name.charAt(0);
            prev.classList.add('flex', 'items-center', 'justify-center', 'text-xl', 'font-bold', 'text-white');
        }
    }

    if (document.getElementById('voice-status')) document.getElementById('voice-status').textContent = '';
    if (document.getElementById('upload-voice-btn')) document.getElementById('upload-voice-btn').disabled = true;

    window.dispatchEvent(new CustomEvent('open-edit-modal'));
}

function setVal(id, val) {
    const el = document.getElementById(id);
    if (el) el.value = val || "";
}

function setCheck(id, val) {
    const el = document.getElementById(id);
    if (el) el.checked = val;
}

function setupVoiceRecorder(renderCallback) {
    const recordBtn = document.getElementById('record-btn');
    const stopBtn = document.getElementById('stop-btn');
    const uploadVoiceBtn = document.getElementById('upload-voice-btn');
    const voiceStatus = document.getElementById('voice-status');

    if (recordBtn) {
        recordBtn.onclick = async () => {
            if (!state.voiceRecorder && typeof VoiceRecorder !== 'undefined') {
                state.voiceRecorder = new VoiceRecorder('recorder-canvas');
            }
            if (!state.voiceRecorder) {
                if (voiceStatus) voiceStatus.textContent = "Recorder not loaded";
                return;
            }

            try {
                await state.voiceRecorder.start();
                recordBtn.classList.add('hidden');
                stopBtn.classList.remove('hidden');
                voiceStatus.textContent = "Recording...";
                uploadVoiceBtn.disabled = true;
            } catch (err) {
                voiceStatus.textContent = "Mic access denied.";
            }
        };
    }

    if (stopBtn) {
        stopBtn.onclick = async () => {
            const result = await state.voiceRecorder.stop();
            if (result) {
                voiceBlob = result.blob;
                voiceWaveform = result.waveform;

                recordBtn.classList.remove('hidden');
                stopBtn.classList.add('hidden');
                voiceStatus.textContent = "Recording captured. Ready to upload.";
                uploadVoiceBtn.disabled = false;
            }
        };
    }

    if (uploadVoiceBtn) {
        uploadVoiceBtn.onclick = async () => {
            if (!voiceBlob) return;
            voiceStatus.textContent = "Uploading...";

            const formData = new FormData();
            formData.append('voice', voiceBlob);
            formData.append('waveform', JSON.stringify(voiceWaveform));

            try {
                const res = await fetch('/profile/voice/upload', {
                    method: 'POST',
                    body: formData
                });
                const data = await res.json();

                if (data.ok) {
                    voiceStatus.textContent = "Uploaded successfully!";
                    voiceStatus.classList.add('text-emerald-400');
                    state.currentUserData.voice_intro_path = data.voice_path;
                    state.currentUserData.voice_waveform_json = JSON.stringify(voiceWaveform);
                    if (renderCallback) renderCallback(state.currentUserData);
                } else {
                    voiceStatus.textContent = "Upload failed.";
                }
            } catch (e) {
                voiceStatus.textContent = "Error uploading.";
            }
        };
    }
}

function setupAvatarUpload(renderCallback) {
    const avatarInput = document.getElementById('avatar-input');
    if (avatarInput) {
        avatarInput.onchange = async (e) => {
            const file = e.target.files[0];
            if (!file) return;

            const formData = new FormData();
            formData.append('avatar', file);

            const prev = document.getElementById('preview-avatar');
            prev.innerHTML = '<i class="ph-bold ph-spinner animate-spin text-white"></i>';
            try {
                const res = await fetch('/profile/avatar', {
                    method: 'POST',
                    body: formData
                });
                const data = await res.json();
                if (data.ok) {
                    prev.style.backgroundImage = `url('${data.avatar_path}')`;
                    prev.innerHTML = '';
                    state.currentUserData.avatar_path = data.avatar_path;
                    if (renderCallback) renderCallback(state.currentUserData);
                } else {
                    alert(data.error || "Upload failed");
                    prev.innerHTML = '❌';
                }
            } catch (err) {
                console.error(err);
                alert("Upload error");
            }
        };
    }
}
