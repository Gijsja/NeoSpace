
// DOM Elements
const wallContainer = document.getElementById('wall-container');
const loadingEl = document.getElementById('loading');
const editModal = document.getElementById('edit-modal');
const editForm = document.getElementById('edit-form');

// State
const urlParams = new URLSearchParams(window.location.search);
const userId = urlParams.get('user_id'); // If null, assume current user
let currentUserData = null;
let stickerManager = null;
let voiceRecorder = null; // VoiceRecorder instance

// Theme Definitions
const themes = {
    'default': 'linear-gradient(135deg, #0f172a 0%, #1e293b 100%)',
    'dark': 'linear-gradient(to bottom, #000000, #111111)',
    'retro': 'linear-gradient(45deg, #2b0a3d, #c53c8d)',
    'zen': 'linear-gradient(to bottom, #1a2f23, #2f4f4f)'
};

async function fetchProfile() {
    const endpoint = userId ? `/profile?user_id=${userId}` : '/profile';
    try {
        const res = await fetch(endpoint);
        if (res.status === 401) {
            window.location.href = '/auth/login';
            return;
        }
        const data = await res.json();
        
        if (data.error) {
            loadingEl.innerHTML = `<div class="text-red-400 font-bold">${data.error}</div>`;
            return;
        }

        currentUserData = data;
        renderProfile(data);
        
        // Init Stickers
        if (!stickerManager) {
            // containerId, isHost, currentUserId, targetUserId
            stickerManager = new StickerManager(
                'sticker-canvas', 
                data.is_own, 
                data.viewer_id, 
                data.user_id
            );
            
            // Show palette if logged in
            if (data.viewer_id) {
                setupPalette();
            }
        }
        stickerManager.setStickers(data.stickers);
        
        loadingEl.classList.add('hidden');
        wallContainer.classList.remove('hidden');
    } catch (err) {
        console.error(err);
        loadingEl.innerHTML = `<div class="text-red-400 font-bold">Failed to load profile (Network Error).</div>`;
    }
}

function renderProfile(data) {
    document.title = `${data.display_name}'s Wall`;
    
    // Text fields
    const displayNameEl = document.getElementById('display-name');
    if (displayNameEl) displayNameEl.textContent = data.display_name;
    
    const handleEl = document.getElementById('username-handle');
    if (handleEl) handleEl.textContent = `@${data.username}`;
    
    // Status & Now
    const statusMsgEl = document.getElementById('status-message');
    if (statusMsgEl) statusMsgEl.textContent = data.status_message || "Just setting up my space...";
    
    const statusEmojiEl = document.getElementById('status-emoji');
    if (statusEmojiEl) statusEmojiEl.textContent = data.status_emoji || "👋";
    
    const nowActivityEl = document.getElementById('now-activity');
    if (nowActivityEl) nowActivityEl.textContent = data.now_activity || "Just chilling...";
    
    // Icon mapping for "Now" type
    const activityIcons = {
        'listening': 'ph-headphones',
        'working': 'ph-laptop',
        'playing': 'ph-game-controller',
        'reading': 'ph-book-open',
        'thinking': 'ph-brain',
        'watching': 'ph-monitor-play'
    };
    const iconClass = activityIcons[data.now_activity_type] || 'ph-star';
    const nowIconEl = document.getElementById('now-activity-type-icon');
    if (nowIconEl) nowIconEl.innerHTML = `<i class="ph-fill ${iconClass}"></i>`;

    const memberSinceEl = document.getElementById('member-since');
    if (memberSinceEl) memberSinceEl.textContent = new Date(data.member_since).toLocaleDateString(undefined, { year: 'numeric', month: 'short' });

    // Avatar
    const avatarEl = document.getElementById('avatar-container');
    const initialEl = document.getElementById('avatar-initial');
    if (avatarEl && initialEl) {
        if (data.avatar_path) {
            avatarEl.style.backgroundImage = `url('${data.avatar_path}')`;
            initialEl.classList.add('hidden');
        } else {
            avatarEl.style.backgroundImage = '';
            initialEl.classList.remove('hidden');
            initialEl.textContent = data.display_name.charAt(0).toUpperCase();
        }
    }

    // Voice Intro
    const voiceSection = document.getElementById('voice-intro-section');
    if (voiceSection) {
        if (data.voice_intro_path) {
            voiceSection.classList.remove('hidden');
            // Parse waveform JSON safely
            let waveform = [];
            try {
                waveform = JSON.parse(data.voice_waveform_json || '[]');
            } catch(e) {}
            
            // Check if VoicePlayer is available
            if (typeof VoicePlayer !== 'undefined') {
                 new VoicePlayer('voice-intro-section', data.voice_intro_path, waveform);
            }
        } else {
            voiceSection.classList.add('hidden');
            voiceSection.innerHTML = ''; 
        }
    }

    // Audio Anthem (Sprint 11)
    setupAnthem(data.anthem_url, data.anthem_autoplay);

    // Theme & Accent
    if (themes[data.theme_preset]) {
        document.getElementById('wall-container').style.background = themes[data.theme_preset];
    }
    document.documentElement.style.setProperty('--color-accent', data.accent_color);
    
    // Interaction
    if (data.is_own) {
        // Show edit controls
        ['edit-avatar-btn', 'edit-profile-btn', 'edit-now-btn'].forEach(id => {
            const el = document.getElementById(id);
            if(el) {
                el.classList.remove('hidden');
                el.onclick = openEditModal; // For now all open main modal
            }
        });
    }
    
    if (data.show_online_status) {
        const onlineEl = document.getElementById('online-indicator');
        if (onlineEl) onlineEl.classList.remove('hidden');
    }
    
    // Pinned Scripts
    renderPinnedScripts(data.pinned_scripts);
}

// --- Edit Logic ---

function openEditModal() {
    if (!currentUserData) return;
    const d = currentUserData;
    
    const inputName = document.getElementById('input-name');
    if (inputName) inputName.value = d.display_name;
    
    const inputBio = document.getElementById('input-bio');
    if (inputBio) inputBio.value = d.bio;
    
    // New Fields
    if(document.getElementById('input-status-msg')) document.getElementById('input-status-msg').value = d.status_message || "";
    if(document.getElementById('input-status-emoji')) document.getElementById('input-status-emoji').value = d.status_emoji || "👋";
    if(document.getElementById('input-now-activity')) document.getElementById('input-now-activity').value = d.now_activity || "";
    if(document.getElementById('input-now-type')) document.getElementById('input-now-type').value = d.now_activity_type || "thinking";

    if(document.getElementById('input-theme')) document.getElementById('input-theme').value = d.theme_preset;
    if(document.getElementById('input-accent')) document.getElementById('input-accent').value = d.accent_color;
    if(document.getElementById('input-public')) document.getElementById('input-public').checked = d.is_public !== false; 
    if(document.getElementById('input-online')) document.getElementById('input-online').checked = d.show_online_status !== false;
    
    // Anthem fields
    if(document.getElementById('input-anthem-url')) document.getElementById('input-anthem-url').value = d.anthem_url || '';
    if(document.getElementById('input-anthem-autoplay')) document.getElementById('input-anthem-autoplay').checked = d.anthem_autoplay !== false;

    // Preview current avatar
    const prev = document.getElementById('preview-avatar');
    if (prev) {
        if (d.avatar_path) prev.style.backgroundImage = `url('${d.avatar_path}')`;
        else {
            prev.style.backgroundImage = '';
            prev.textContent = d.display_name.charAt(0);
            prev.classList.add('flex', 'items-center', 'justify-center', 'text-xl', 'font-bold', 'text-white');
        }
    }
    
    // Reset Voice UI
    if (document.getElementById('voice-status')) document.getElementById('voice-status').textContent = '';
    if (document.getElementById('upload-voice-btn')) document.getElementById('upload-voice-btn').disabled = true;

    editModal.classList.remove('hidden');
}

document.querySelectorAll('.close-modal').forEach(b => {
    b.onclick = () => {
        editModal.classList.add('hidden');
        if (voiceRecorder) voiceRecorder.stop(); // Ensure recording stops if modal closed
    };
});

// --- Voice Recorder Logic ---
let voiceBlob = null;
let voiceWaveform = null;

const recordBtn = document.getElementById('record-btn');
const stopBtn = document.getElementById('stop-btn');
const uploadVoiceBtn = document.getElementById('upload-voice-btn');
const voiceStatus = document.getElementById('voice-status');

if (recordBtn) {
    recordBtn.onclick = async () => {
        if (!voiceRecorder) {
            voiceRecorder = new VoiceRecorder('recorder-canvas');
        }
        
        try {
            await voiceRecorder.start();
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
            const result = await voiceRecorder.stop();
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
                    currentUserData.voice_intro_path = data.voice_path;
                    currentUserData.voice_waveform_json = JSON.stringify(voiceWaveform);
                    renderProfile(currentUserData); // Update bg loop
                } else {
                    voiceStatus.textContent = "Upload failed.";
                }
            } catch(e) {
                voiceStatus.textContent = "Error uploading.";
            }
    };
}

// Handle Avatar Upload independently or as part of submit?
// Let's do instant upload for avatar to simplify
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
                // Update preview
                prev.style.backgroundImage = `url('${data.avatar_path}')`;
                prev.innerHTML = '';
                // Also update main view live
                currentUserData.avatar_path = data.avatar_path;
                renderProfile(currentUserData);
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

if (editForm) {
    editForm.onsubmit = async (e) => {
        e.preventDefault();
        const formData = new FormData(editForm);
        const payload = Object.fromEntries(formData.entries());
        
        // checkbox handling
        payload.is_public = formData.get('is_public') === 'on';
        payload.show_online_status = formData.get('show_online_status') === 'on';
        payload.anthem_autoplay = formData.get('anthem_autoplay') === 'on';

        try {
            const res = await fetch('/profile/update', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(payload)
            });
            const data = await res.json();
            if (data.ok) {
                editModal.classList.add('hidden');
                fetchProfile(); // Reload
            } else {
                alert(data.error || "Update failed");
            }
        } catch (err) {
            alert("Update error");
        }
    };
}

// =============================================
// AUDIO ANTHEM (Sprint 11)
// =============================================
let anthemMuted = false;
const anthemPlayer = document.getElementById('anthem-player');
const anthemToggle = document.getElementById('anthem-toggle');
const anthemIcon = document.getElementById('anthem-icon');

function setupAnthem(url, autoplay) {
    if (!url) {
        if (anthemToggle) anthemToggle.classList.add('hidden');
        if (anthemPlayer) {
            anthemPlayer.pause();
            anthemPlayer.src = '';
        }
        return;
    }
    
    if (anthemPlayer) anthemPlayer.src = url;
    if (anthemToggle) anthemToggle.classList.remove('hidden');
    
    if (autoplay) {
        // Try to play (may be blocked by browser policy)
        if (anthemPlayer) {
            anthemPlayer.play().then(() => {
                updateAnthemIcon(false);
            }).catch(() => {
                // Autoplay blocked - show as muted, user can click to play
                anthemMuted = true;
                updateAnthemIcon(true);
            });
        }
    } else {
        anthemMuted = true;
        updateAnthemIcon(true);
    }
}

function updateAnthemIcon(muted) {
    if (!anthemIcon || !anthemToggle) return;
    if (muted) {
        anthemIcon.className = 'ph-bold ph-speaker-x text-xl';
        anthemToggle.classList.add('bg-slate-600/80');
        anthemToggle.classList.remove('bg-purple-600/80');
    } else {
        anthemIcon.className = 'ph-bold ph-speaker-high text-xl';
        anthemToggle.classList.remove('bg-slate-600/80');
        anthemToggle.classList.add('bg-purple-600/80');
    }
}

if (anthemToggle) {
    anthemToggle.onclick = () => {
        anthemMuted = !anthemMuted;
        if (anthemMuted) {
            anthemPlayer.pause();
        } else {
            anthemPlayer.play().catch(() => {});
        }
        updateAnthemIcon(anthemMuted);
    };
}

function setupPalette() {
    const palette = document.getElementById('sticker-palette');
    if (palette) palette.classList.remove('hidden');
    
    // From global STICKERS_PRESETS in wall.js
    if (palette && window.STICKERS_PRESETS) {
        palette.innerHTML = '';
        window.STICKERS_PRESETS.forEach(char => {
            const el = document.createElement('div');
            el.className = 'text-3xl hover:scale-125 transition cursor-grab active:cursor-grabbing p-2 shrink-0';
            el.innerText = char;
            el.draggable = true;
            el.ondragstart = (e) => {
                // Pass to manager logic if needed, or just let manager handle dragstart globally?
                // Actually global dragstart might be tricky if not on canvas.
                // Let's attach handler manually here since they are outside canvas
                // But wait, manager.handleDragStart listens on elements. Pallete items are new.
                // We need a way to hook into the manager's drag start logic for new items.
                // Implemented: Manager expects e.target.innerText for new items.
            };
            // Re-attaching the same handler logic?
            el.addEventListener('dragstart', (e) => {
                // We need to manually construct the data transfer here
                e.dataTransfer.setData('text/plain', JSON.stringify({
                    type: 'new',
                    sticker: char,
                    offsetX: 20, // Center approx
                    offsetY: 20
                }));
            });
            
            palette.appendChild(el);
        });
    }
}

// =============================================
// PINNED SCRIPTS RENDERING (Masonry)
// =============================================
function renderPinnedScripts(scripts) {
    if (!scripts || scripts.length === 0) {
        const pinnedSection = document.getElementById('pinned-scripts-section');
        if (pinnedSection) pinnedSection.classList.add('hidden');
        return;
    }
    
    const section = document.getElementById('pinned-scripts-section');
    const grid = document.getElementById('pinned-scripts-grid');
    if (section) section.classList.remove('hidden');
    if (grid) {
        grid.innerHTML = '';
        
        // Switch grid to masonry columns via CSS class if not already set
        grid.className = 'columns-1 md:columns-3 gap-6 space-y-6';
        
        scripts.forEach(script => {
            const card = document.createElement('div');
            
            // Random aspect ratio for masonry effect (Tall, Square, Wide)
            // We'll use a pseudo-random determined by script ID so it's stable
            const heights = ['h-64', 'h-80', 'h-56'];
            const heightClass = heights[script.id % heights.length];
            
            card.className = `glass-panel-interactive rounded-xl overflow-hidden relative group ${heightClass} break-inside-avoid transition-all duration-300 hover:shadow-glow-md mb-6 w-full`;
            
            // HTML structure for immersive card
            card.innerHTML = `
                <!-- Header Overlay -->
                <div class="absolute top-0 left-0 right-0 p-3 flex justify-between items-start z-20 pointer-events-none bg-gradient-to-b from-black/80 to-transparent">
                    <h4 class="font-bold text-white text-shadow-sm truncate pr-2">${script.title}</h4>
                    <span class="text-[10px] uppercase font-mono bg-black/50 px-1.5 py-0.5 rounded text-slate-300 border border-white/10 backdrop-blur">${script.script_type}</span>
                </div>

                <!-- Script Container -->
                <div class="script-container absolute inset-0 bg-slate-900 z-10">
                    <!-- Placeholder / Play Trigger -->
                        <div class="placeholder absolute inset-0 flex items-center justify-center cursor-pointer group-hover:bg-white/5 transition z-20">
                            <div class="w-12 h-12 rounded-full bg-bbs-accent/20 border border-bbs-accent/50 flex items-center justify-center backdrop-blur group-hover:scale-110 transition shadow-glow">
                            <i class="ph-fill ph-play text-bbs-accent text-xl"></i>
                            </div>
                            <div class="absolute bottom-4 left-0 right-0 text-center text-xs text-slate-400 opacity-0 group-hover:opacity-100 transition">
                            Click to Run
                            </div>
                    </div>
                </div>
            `;
            
            const placeholder = card.querySelector('.placeholder');
            placeholder.onclick = (e) => {
                e.stopPropagation();
                activateScript(card, script);
            };
            
            grid.appendChild(card);
        });
    }
}

async function activateScript(card, script) {
    const container = card.querySelector('.script-container');
    const placeholder = card.querySelector('.placeholder');
    
    // Loading state
    placeholder.innerHTML = '<i class="ph-bold ph-spinner animate-spin text-bbs-accent text-2xl"></i>';
    
    // Fetch content if not provided in list (we need full content)
    // The profile endpoint might perform optimization and not send full content for huge scripts
    // But currently it does include full content via join if we check mutations/profile.py
    // Actually get_pinned_scripts returns id, title, script_type... 
    // We need to fetch full content!
    
    try {
        const res = await fetch(`/scripts/get?id=${script.id}`);
        const data = await res.json();
        
        if (!data.ok) {
            placeholder.innerHTML = '<span class="text-red-400 text-xs">Failed</span>';
            return;
        }
        
        const fullScript = data.script;
        const mode = fullScript.script_type || 'p5';
        
        // Construct Iframe
        const iframe = document.createElement('iframe');
        iframe.className = "w-full h-full border-none bg-black absolute inset-0 z-30 animate-fade-in";
        iframe.setAttribute('sandbox', 'allow-scripts');
        
        // Generate iframe content with autosize
        let html = '';
        if (mode === 'p5') {
            html = `<!DOCTYPE html>
<html>
<head>
<style>body { margin: 0; overflow: hidden; }</style>
<script src="https://cdnjs.cloudflare.com/ajax/libs/p5.js/1.9.0/p5.min.js"><\/script>
</head>
<body>
<script>
// Force P5 to fit container
function windowResized() {
    if (typeof resizeCanvas === 'function') resizeCanvas(window.innerWidth, window.innerHeight);
}

try {
    ${fullScript.content}
    
    // Inject auto-resize if not present
    if (!${fullScript.content.includes('setup')}) {
        // If they wrote raw p5 without setup (global mode), wrapper might be needed
        // But assuming standard p5 instance mode or global mode:
        // We'll leave it to user code, but default p5 canvas matches display size usually
    }
} catch (e) {
    document.body.innerHTML = '<pre style="color:red; padding:10px; font-size:10px;">' + e.toString() + '</pre>';
}
<\/script>
</body>
</html>`;
        } else if (mode === 'three') {
            html = `<!DOCTYPE html>
<html>
<head><style>body { margin: 0; overflow: hidden; }</style></head>
<body>
<script type="module">
try {
    ${fullScript.content}
} catch (e) {
    document.body.innerHTML = '<pre style="color:red; padding:10px; font-size:10px;">' + e.toString() + '</pre>';
}
<\/script>
</body>
</html>`;
        } else {
            html = `<!DOCTYPE html><html><body style="margin:0;overflow:hidden;color:#fff;font-family:monospace;font-size:12px;"><script>${fullScript.content}<\/script></body></html>`;
        }
        
        // Clear placeholder and inject iframe
        container.innerHTML = '';
        container.appendChild(iframe);
        
        // Write content safely using srcdoc (avoids cross-origin issues with sandbox)
        iframe.srcdoc = html;
        
        // Add "Stop" button overlay on hover
        const stopBtn = document.createElement('button');
        stopBtn.className = "absolute top-3 right-3 z-40 bg-black/50 hover:bg-red-500/80 text-white p-1 rounded backdrop-blur opacity-0 group-hover:opacity-100 transition";
        stopBtn.innerHTML = '<i class="ph-bold ph-stop"></i>';
        stopBtn.title = "Stop Script";
        stopBtn.onclick = (e) => {
            e.stopPropagation();
            // Re-render this card to reset
            renderPinnedScripts([script]); // This is a bit heavy-handed, actually better to just reset this card's innerHTML
            // But simpler for now to revert to renderPinnedScripts logic for single item? 
            // Let's just reload the whole list to be safe or re-call render for that item.
            // For now, reload page section:
            fetchProfile();
        };
        card.appendChild(stopBtn);
        
    } catch (err) {
            placeholder.innerHTML = '<span class="text-red-400 text-xs">Error</span>';
            console.error(err);
    }
}

// Close preview modal logic if it exists (seems unused in wall.html but left in for safety)
const scriptPreviewModal = document.getElementById('script-preview-modal');
const closePreviewBtn = document.getElementById('close-preview');
if (scriptPreviewModal && closePreviewBtn) {
    closePreviewBtn.onclick = () => {
        scriptPreviewModal.classList.add('hidden');
        const previewFrame = document.getElementById('preview-iframe');
        if (previewFrame) previewFrame.srcdoc = ''; // Stop execution
    };
}

// Init
fetchProfile();
