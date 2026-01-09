/**
 * WallModules.js
 * Renders and manages the modular wall grid.
 */

import { state } from './WallState.js';
import { deleteModule, fetchScriptContent } from './WallNetwork.js'; // Need to add fetch to Network

export function renderWallModules(modules) {
    const section = document.getElementById('wall-modules-section');
    const grid = document.getElementById('wall-modules-grid');

    if (!modules || modules.length === 0) {
        if (section) section.classList.add('hidden');
        return;
    }

    if (section) section.classList.remove('hidden');

    if (grid) {
        grid.innerHTML = '';
        grid.className = 'columns-1 md:columns-2 lg:columns-3 gap-6 space-y-6';

        modules.forEach(mod => {
            let card = createModuleCard(mod);
            if (card) grid.appendChild(card);
        });

        if (typeof hljs !== 'undefined') {
            grid.querySelectorAll('pre code').forEach((block) => {
                hljs.highlightElement(block);
            });
        }
    }
}

export function appendWallModules(modules) {
    const grid = document.getElementById('wall-modules-grid');
    if (!grid || !modules) return;

    modules.forEach(mod => {
        let card = createModuleCard(mod);
        if (card) grid.appendChild(card);
    });

    if (typeof hljs !== 'undefined') {
        grid.querySelectorAll('pre code').forEach((block) => {
            hljs.highlightElement(block);
        });
    }
}

function createModuleCard(mod) {
    let card = document.createElement('div');
    card.dataset.moduleId = mod.id;
    card.dataset.moduleType = mod.module_type;
    card.className = `glass-panel-interactive rounded-xl overflow-hidden relative group break-inside-avoid transition-all duration-300 hover:shadow-glow-md mb-6 w-full`;

    // Switch on type
    if (mod.module_type === 'script' && mod.script_details) {
        renderScriptModule(card, mod);
    } else if (mod.module_type === 'text') {
        renderTextModule(card, mod);
    } else if (mod.module_type === 'image') {
        renderImageModule(card, mod);
    } else if (mod.module_type === 'link') {
        renderLinkModule(card, mod);
    } else if (mod.module_type === 'audio') {
        renderAudioModule(card, mod);
    } else if (mod.module_type === 'voice_note') {
        renderVoiceModule(card, mod);
    } else {
        return null; // Unknown type
    }

    // Owner Actions
    if (state.currentUserData && state.currentUserData.is_own) {
        const menuBtn = document.createElement('button');
        menuBtn.className = 'module-menu-btn absolute top-2 right-2 z-40 w-8 h-8 rounded-full bg-black/50 hover:bg-black/80 text-white flex items-center justify-center opacity-0 group-hover:opacity-100 transition backdrop-blur';
        menuBtn.innerHTML = '<i class="ph-bold ph-dots-three-vertical"></i>';
        menuBtn.onclick = (e) => {
            e.stopPropagation();
            showModuleMenu(mod, menuBtn);
        };
        card.appendChild(menuBtn);
    }

    return card;
}

function renderVoiceModule(card, mod) {
    const src = mod.content.url;
    const title = mod.content.title || "Voice Note";
    card.innerHTML = getGhettoblasterTemplate(src, title, true);
}


function renderScriptModule(card, mod) {
    const script = mod.script_details;
    const heights = ['h-64', 'h-80', 'h-56'];
    const heightClass = heights[mod.id % heights.length];
    card.classList.add(heightClass);

    card.innerHTML = `
        <div class="absolute top-0 left-0 right-0 p-3 flex justify-between items-start z-20 pointer-events-none bg-gradient-to-b from-black/80 to-transparent">
            <h4 class="font-bold text-white text-shadow-sm truncate pr-2">${script.title}</h4>
            <span class="text-[10px] uppercase font-mono bg-black/50 px-1.5 py-0.5 rounded text-slate-300 border border-white/10 backdrop-blur">${script.script_type}</span>
        </div>
        <div class="script-container absolute inset-0 bg-slate-900 z-10">
            <div class="placeholder absolute inset-0 flex items-center justify-center cursor-pointer group-hover:bg-white/5 transition z-20">
                 <div class="w-12 h-12 rounded-full bg-bbs-accent/20 border border-bbs-accent/50 flex items-center justify-center backdrop-blur group-hover:scale-110 transition shadow-glow">
                    <i class="ph-fill ph-play text-bbs-accent text-xl"></i>
                 </div>
                 <div class="absolute bottom-4 left-0 right-0 text-center text-xs text-slate-400 opacity-0 group-hover:opacity-100 transition">Click to Run</div>
            </div>
        </div>
    `;

    const placeholder = card.querySelector('.placeholder');
    placeholder.onclick = (e) => {
        e.stopPropagation();
        activateScript(card, script);
    };
}

function renderTextModule(card, mod) {
    card.classList.add('bg-bbs-surface/50');
    const content = mod.content.text || "";
    let htmlContent = content;
    if (typeof marked !== 'undefined') htmlContent = marked.parse(content);
    if (typeof DOMPurify !== 'undefined') htmlContent = DOMPurify.sanitize(htmlContent);

    card.innerHTML = `<div class="p-5"><div class="prose prose-invert prose-sm max-w-none text-slate-300 leading-relaxed font-mono text-sm break-words module-text-content">${htmlContent}</div></div>`;
}

function renderImageModule(card, mod) {
    card.innerHTML = `<img src="${mod.content.url}" class="w-full h-auto object-cover" loading="lazy" />`;
}

function renderLinkModule(card, mod) {
    let hostname = '';
    try { hostname = new URL(mod.content.url).hostname; } catch (e) { hostname = mod.content.url; }

    // Default to 'simple' if not set
    const style = mod.style ? (mod.style.link_style || 'simple') : 'simple';
    const title = mod.content.title || hostname;
    const thumb = mod.content.thumbnail;

    if (style === 'button') {
        // BUTTON STYLE
        card.innerHTML = `
            <a href="${mod.content.url}" target="_blank" class="block w-full text-center py-4 bg-electric-blue text-black font-black uppercase hover:bg-hot-pink hover:text-white border-none transition shadow-none flex items-center justify-center gap-2 group-hover:scale-[1.02]">
                <span>${title}</span>
                <i class="ph-bold ph-arrow-up-right"></i>
            </a>
        `;
        // Remove default panel classes potentially? Or keep them. Keep them for consistency.
        card.classList.remove('glass-panel-interactive', 'rounded-xl', 'overflow-hidden');
        card.classList.add('border-2', 'border-black', 'bg-electric-blue', 'shadow-hard-sm');

    } else if (style === 'card') {
        // CARD STYLE
        // Ensure card has height
        card.classList.remove('glass-panel-interactive');
        card.classList.add('bg-white', 'border-2', 'border-black', 'shadow-hard-sm', 'hover:shadow-hard', 'transition-shadow');

        let imgHtml = '';
        if (thumb) {
            imgHtml = `<div class="w-full h-32 bg-gray-200 border-b-2 border-black bg-cover bg-center" style="background-image: url('${thumb}');"></div>`;
        } else {
            // Fallback pattern
            imgHtml = `<div class="w-full h-32 bg-pattern-dots border-b-2 border-black flex items-center justify-center"><i class="ph-duotone ph-link text-4xl text-gray-400"></i></div>`;
        }

        card.innerHTML = `
            <a href="${mod.content.url}" target="_blank" class="block h-full group/link">
                ${imgHtml}
                <div class="p-3">
                    <h4 class="font-bold text-black text-sm uppercase leading-tight mb-1 group-hover/link:underline line-clamp-2">${title}</h4>
                    <p class="text-[10px] text-slate-500 truncate font-mono">${hostname}</p>
                </div>
            </a>
        `;
    } else {
        // SIMPLE STYLE (Default)
        // Keep existing look but refine logic
        card.innerHTML = `
            <a href="${mod.content.url}" target="_blank" class="block p-4 bg-white/5 hover:bg-white/10 transition">
                <div class="flex items-center gap-3">
                    <div class="w-10 h-10 border-2 border-black bg-white flex items-center justify-center shrink-0 shadow-hard-sm">
                        <i class="ph-bold ph-link text-black"></i>
                    </div>
                    <div class="min-w-0">
                        <h4 class="font-bold text-sm text-slate-200 truncate group-hover:text-white transition">${title}</h4>
                        <p class="text-xs text-slate-500 truncate">${hostname}</p>
                    </div>
                </div>
            </a>
        `;
    }
}

function renderAudioModule(card, mod) {
    const title = mod.content.title || "Audio Track";
    card.innerHTML = getGhettoblasterTemplate(mod.content.url, title, false);
}

export function showModuleMenu(mod, anchorBtn) {
    if (window.activeModuleMenu) {
        window.activeModuleMenu.remove();
        window.activeModuleMenu = null;
    }

    const menu = document.createElement('div');
    menu.className = 'module-context-menu absolute z-50 bg-slate-800 border border-slate-600 rounded-lg shadow-xl py-1 min-w-[120px] animate-pop';
    menu.innerHTML = `
        <button class="edit-module-btn w-full text-left px-3 py-2 text-sm text-slate-200 hover:bg-slate-700 flex items-center gap-2 transition">
            <i class="ph-bold ph-pencil-simple"></i> Edit
        </button>
        <button class="delete-module-btn w-full text-left px-3 py-2 text-sm text-red-400 hover:bg-red-500/20 flex items-center gap-2 transition">
            <i class="ph-bold ph-trash"></i> Delete
        </button>
        <div class="h-px bg-slate-700 my-1"></div>
        <button class="report-module-btn w-full text-left px-3 py-2 text-sm text-yellow-500 hover:bg-yellow-500/20 flex items-center gap-2 transition">
            <i class="ph-bold ph-warning-octagon"></i> Report
        </button>
    `;

    const rect = anchorBtn.getBoundingClientRect();
    menu.style.position = 'fixed';
    menu.style.top = `${rect.bottom + 4}px`;
    menu.style.right = `${window.innerWidth - rect.right}px`;

    document.body.appendChild(menu);
    window.activeModuleMenu = menu;

    menu.querySelector('.edit-module-btn').onclick = () => {
        menu.remove();
        window.activeModuleMenu = null;
        openEditModuleModal(mod);
    };

    menu.querySelector('.delete-module-btn').onclick = async () => {
        menu.remove();
        window.activeModuleMenu = null;
        if (confirm('Delete this module?')) {
            await deleteModule(mod.id); // Network handles reload
        }
    };

    menu.querySelector('.report-module-btn').onclick = async () => {
        menu.remove();
        window.activeModuleMenu = null;
        const reason = prompt("What is the reason for reporting this module?");
        if (reason) {
            try {
                const res = await fetch('/admin/report', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        content_type: 'post',
                        content_id: String(mod.id),
                        reason: reason
                    })
                });
                const data = await res.json();
                if (data.success) alert("Report submitted. Thank you.");
                else alert("Failed to submit report: " + (data.error || "Unknown error"));
            } catch (e) {
                alert("Network error");
            }
        }
    };

    const closeHandler = (e) => {
        if (!menu.contains(e.target) && e.target !== anchorBtn) {
            menu.remove();
            window.activeModuleMenu = null;
            document.removeEventListener('click', closeHandler);
        }
    };
    setTimeout(() => document.addEventListener('click', closeHandler), 0);
}

export async function activateScript(card, script) {
    const container = card.querySelector('.script-container');
    const placeholder = card.querySelector('.placeholder');

    placeholder.innerHTML = '<i class="ph-bold ph-spinner animate-spin text-bbs-accent text-2xl"></i>';

    try {
        const data = await fetchScriptContent(script.id);
        if (!data.ok) {
            placeholder.innerHTML = '<span class="text-red-400 text-xs">Failed</span>';
            return;
        }

        const fullScript = data.script;
        const mode = fullScript.script_type || 'p5';

        const iframe = document.createElement('iframe');
        iframe.className = "w-full h-full border-none bg-black absolute inset-0 z-30 animate-fade-in";
        iframe.setAttribute('sandbox', 'allow-scripts');

        // P5 Support
        let html = '';
        if (mode === 'p5') {
            html = `<!DOCTYPE html><html><head><style>body { margin: 0; overflow: hidden; }</style><script src="https://cdnjs.cloudflare.com/ajax/libs/p5.js/1.9.0/p5.min.js"><\/script></head><body><script>function windowResized(){if(typeof resizeCanvas==='function')resizeCanvas(window.innerWidth,window.innerHeight);} try{${fullScript.content}}catch(e){document.body.innerHTML='<pre style="color:red">'+e.toString()+'</pre>'}</script></body></html>`;
        } else if (mode === 'three') {
            html = `<!DOCTYPE html><html><head><style>body { margin: 0; overflow: hidden; }</style></head><body><script type="module">try{${fullScript.content}}catch(e){document.body.innerHTML='<pre style="color:red">'+e.toString()+'</pre>'}</script></body></html>`;
        } else {
            html = `<!DOCTYPE html><html><body style="margin:0;overflow:hidden;color:#fff;font-family:monospace;font-size:12px;"><script>${fullScript.content}<\/script></body></html>`;
        }

        container.innerHTML = '';
        container.appendChild(iframe);
        iframe.srcdoc = html;

        const stopBtn = document.createElement('button');
        stopBtn.className = "absolute top-3 right-3 z-40 bg-black/50 hover:bg-red-500/80 text-white p-1 rounded backdrop-blur opacity-0 group-hover:opacity-100 transition";
        stopBtn.innerHTML = '<i class="ph-bold ph-stop"></i>';
        stopBtn.onclick = (e) => {
            e.stopPropagation();
            import('./WallNetwork.js').then(n => n.fetchProfileData()).then(data => {
                // Actually need to trigger render, but just reloading the page section might be overkill.
                // Simpler: reload page
                window.location.reload();
            });
        };
        card.appendChild(stopBtn);

    } catch (err) {
        placeholder.innerHTML = '<span class="text-red-400 text-xs">Error</span>';
        console.error(err);
    }
}

export function openEditModuleModal(mod) {
    const modal = document.getElementById('add-module-modal');
    const form = document.getElementById('add-module-form');
    if (!modal || !form) return;

    const typeInput = document.getElementById('new-module-type');
    typeInput.value = mod.module_type;

    document.querySelectorAll('.module-type-btn').forEach(btn => {
        if (btn.dataset.type === mod.module_type) btn.click();
    });

    if (mod.module_type === 'text') {
        if (form.querySelector('[name="text_content"]')) form.querySelector('[name="text_content"]').value = mod.content.text || '';
    } else if (mod.module_type === 'image') {
        if (form.querySelector('[name="image_url"]')) form.querySelector('[name="image_url"]').value = mod.content.url || '';
    } else if (mod.module_type === 'link') {
        if (form.querySelector('[name="link_url"]')) form.querySelector('[name="link_url"]').value = mod.content.url || '';
        if (form.querySelector('[name="link_title"]')) form.querySelector('[name="link_title"]').value = mod.content.title || '';
        if (form.querySelector('[name="link_thumb"]')) form.querySelector('[name="link_thumb"]').value = mod.content.thumbnail || '';
        if (form.querySelector('[name="link_style"]')) form.querySelector('[name="link_style"]').value = (mod.style && mod.style.link_style) ? mod.style.link_style : 'simple';
    } else if (mod.module_type === 'audio') {
        if (form.querySelector('[name="audio_url"]')) form.querySelector('[name="audio_url"]').value = mod.content.url || '';
        if (form.querySelector('[name="audio_title"]')) form.querySelector('[name="audio_title"]').value = mod.content.title || '';
    }

    form.dataset.editId = mod.id;

    const submitBtn = form.querySelector('button[type="submit"]');
    if (submitBtn) submitBtn.innerHTML = '<i class="ph-bold ph-check"></i> Save Changes';

    modal.classList.remove('hidden');
}

export function setupModuleForm(callbacks) {
    const addModuleBtn = document.getElementById('add-module-btn');
    const addModuleModal = document.getElementById('add-module-modal');
    const addModuleForm = document.getElementById('add-module-form');
    const moduleTypeBtns = document.querySelectorAll('.module-type-btn');

    if (addModuleBtn) {
        addModuleBtn.onclick = () => {
            if (!addModuleModal) return;
            addModuleModal.classList.remove('hidden');
            // Reset form for add mode
            if (addModuleForm) {
                addModuleForm.reset();
                delete addModuleForm.dataset.editId;
                const submitBtn = addModuleForm.querySelector('button[type="submit"]');
                if (submitBtn) submitBtn.innerHTML = '<i class="ph-bold ph-plus"></i> Add Block';
            }
        };
    }

    document.querySelectorAll('.close-add-modal').forEach(b => {
        b.onclick = () => {
            addModuleModal.classList.add('hidden');
        };
    });

    // Voice Recorder Setup
    setupVoiceRecorder();

    // Type Switching
    moduleTypeBtns.forEach(btn => {
        btn.onclick = () => {
            // Reset styles
            moduleTypeBtns.forEach(b => {
                b.classList.remove('bg-bbs-accent', 'text-white', 'border-bbs-accent');
                b.classList.add('bg-white/5', 'border-transparent');
                b.querySelector('i').classList.remove('text-white');
                b.querySelector('i').classList.add('text-slate-300');
            });

            // Active Style
            btn.classList.remove('bg-white/5', 'border-transparent');
            btn.classList.add('bg-bbs-accent', 'text-white', 'border-bbs-accent');
            btn.querySelector('i').classList.remove('text-slate-300');
            btn.querySelector('i').classList.add('text-white');

            const type = btn.dataset.type;
            document.getElementById('new-module-type').value = type;

            // Show/Hide Fields
            ['text', 'image', 'link', 'audio', 'voice'].forEach(t => {
                const el = document.getElementById(`fields-${t}`);
                if (t === type) el.classList.remove('hidden');
                else el.classList.add('hidden');
            });
        };
    });

    // Init first type
    if (moduleTypeBtns.length > 0) moduleTypeBtns[0].click();

    if (addModuleForm) {
        addModuleForm.onsubmit = async (e) => {
            e.preventDefault();
            const formData = new FormData(addModuleForm);
            const type = formData.get('module_type');
            const editId = addModuleForm.dataset.editId;

            const payload = {
                module_type: type,
                content: {},
                style: {}
            };

            if (type === 'text') {
                payload.content.text = formData.get('text_content');
            } else if (type === 'image') {
                payload.content.url = formData.get('image_url');
            } else if (type === 'link') {
                payload.content.url = formData.get('link_url');
                payload.content.title = formData.get('link_title');
                payload.content.thumbnail = formData.get('link_thumb');
                payload.style.link_style = formData.get('link_style');
            } else if (type === 'audio') {
                payload.content.url = formData.get('audio_url');
                payload.content.title = formData.get('audio_title');
            } else if (type === 'voice') {
                payload.module_type = 'voice_note';
                payload.content.url = formData.get('voice_url');
                payload.content.title = "Voice Note " + new Date().toLocaleTimeString();
            }

            try {
                let endpoint = '/wall/post/add';
                if (editId) {
                    endpoint = '/wall/post/update';
                    payload.id = parseInt(editId);
                } else {
                    payload.display_order = 999;
                }

                const res = await fetch(endpoint, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(payload)
                });
                const data = await res.json();

                if (data.ok) {
                    addModuleModal.classList.add('hidden');
                    addModuleForm.reset();
                    delete addModuleForm.dataset.editId;
                    if (callbacks.onSuccess) callbacks.onSuccess();
                } else {
                    alert(data.error || "Failed");
                }
            } catch (err) {
                console.error(err);
                alert("Network error");
            }
        };
    }
}

function setupVoiceRecorder() {
    const recordBtn = document.getElementById('btn-record-note');
    const stopBtn = document.getElementById('btn-stop-note');
    const canvas = document.getElementById('voice-module-canvas');
    const status = document.getElementById('voice-module-status');
    const urlInput = document.getElementById('voice-module-url');
    const previewArea = document.getElementById('voice-note-preview');
    const audioEl = document.getElementById('voice-note-audio-el');
    const retryBtn = document.getElementById('btn-reset-note');

    if (!recordBtn || !canvas) return;

    let mediaRecorder;
    let chunks = [];
    let animationId;

    const canvasCtx = canvas.getContext('2d');

    recordBtn.onclick = async () => {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            mediaRecorder = new MediaRecorder(stream);
            chunks = [];

            mediaRecorder.ondataavailable = (e) => chunks.push(e.data);

            mediaRecorder.onstop = async () => {
                const blob = new Blob(chunks, { 'type': 'audio/webm; codecs=opus' });
                // Upload
                status.textContent = "Uploading...";
                const formData = new FormData();
                formData.append('file', blob, 'voicenote.webm');

                try {
                    const res = await fetch('/wall/post/upload', { method: 'POST', body: formData });
                    const data = await res.json();
                    if (data.ok) {
                        urlInput.value = data.url;
                        audioEl.src = data.url;
                        previewArea.classList.remove('hidden');
                        status.textContent = "Ready to post.";
                        status.className = "text-[10px] text-center text-emerald-400 h-4";
                    } else {
                        status.textContent = "Upload failed.";
                        status.className = "text-[10px] text-center text-red-400 h-4";
                    }
                } catch (e) {
                    console.error(e);
                    status.textContent = "Network error.";
                }

                stream.getTracks().forEach(track => track.stop());
                cancelAnimationFrame(animationId);
                canvasCtx.clearRect(0, 0, canvas.width, canvas.height); // Clear
            };

            mediaRecorder.start();
            recordBtn.classList.add('hidden');
            stopBtn.classList.remove('hidden');
            status.textContent = "Recording...";
            status.className = "text-[10px] text-center text-rose-400 h-4 animate-pulse";

            // Visualizer
            const audioCtx = new (window.AudioContext || window.webkitAudioContext)();
            const source = audioCtx.createMediaStreamSource(stream);
            const analyzer = audioCtx.createAnalyser();
            analyzer.fftSize = 256;
            source.connect(analyzer);
            const bufferLength = analyzer.frequencyBinCount;
            const dataArray = new Uint8Array(bufferLength);

            const draw = () => {
                animationId = requestAnimationFrame(draw);
                analyzer.getByteFrequencyData(dataArray);
                canvasCtx.fillStyle = '#0f172a';
                canvasCtx.fillRect(0, 0, canvas.width, canvas.height);

                const barWidth = (canvas.width / bufferLength) * 2.5;
                let barHeight;
                let x = 0;

                for (let i = 0; i < bufferLength; i++) {
                    barHeight = dataArray[i] / 2;
                    canvasCtx.fillStyle = `rgb(${barHeight + 100}, 50, 50)`;
                    canvasCtx.fillRect(x, canvas.height - barHeight / 2, barWidth, barHeight / 2); // Centered
                    x += barWidth + 1;
                }
            };
            draw();

        } catch (err) {
            console.error(err);
            alert("Microphone access denied or not supported.");
        }
    };

    stopBtn.onclick = () => {
        if (mediaRecorder && mediaRecorder.state !== 'inactive') {
            mediaRecorder.stop();
            stopBtn.classList.add('hidden');
            recordBtn.classList.remove('hidden');
        }
    };

    retryBtn.onclick = () => {
        urlInput.value = '';
        previewArea.classList.add('hidden');
        status.textContent = '';
    };
}

export function getGhettoblasterTemplate(src, title, isVoice = false) {
    const label = isVoice ? "VOICE NOTE" : "AUDIO TRACK";
    const subLabel = isVoice ? "REC" : "HI-FI";
    const accent = isVoice ? "text-rose-400" : "text-cyan-400";
    const accentBg = isVoice ? "bg-rose-500" : "bg-cyan-500";
    const accentShadow = isVoice ? "shadow-[0_0_10px_rgba(251,113,133,0.8)]" : "shadow-[0_0_10px_rgba(34,211,238,0.8)]";

    // Safety check for src
    const safeSrc = src ? src.replace(/"/g, '&quot;') : '';
    const safeTitle = title ? title.replace(/</g, '&lt;').replace(/>/g, '&gt;') : 'Unknown Track';

    return `
    <div x-data="{ 
            playing: false, 
            audio: null, 
            progress: 0, 
            duration: 0,
            volume: 0.8,
            init() {
                this.audio = this.$refs.audioEl;
                if(this.audio) {
                    this.audio.volume = this.volume;
                    // Native audio events
                    this.audio.addEventListener('loadedmetadata', () => {
                        this.duration = this.audio.duration;
                    });
                    this.audio.addEventListener('timeupdate', () => {
                        this.progress = (this.audio.currentTime / this.duration) * 100;
                    });
                    this.audio.addEventListener('ended', () => {
                        this.playing = false;
                        this.progress = 0;
                    });
                }
            },
            toggle() {
                if (this.playing) this.pause();
                else this.play();
            },
            play() {
                if(this.audio) {
                    this.audio.play();
                    this.playing = true;
                }
            },
            pause() {
                if(this.audio) {
                    this.audio.pause();
                    this.playing = false;
                }
            },
            seek(e) {
                const rect = e.target.getBoundingClientRect();
                const x = e.clientX - rect.left;
                const per = x / rect.width;
                if(this.duration && this.audio) this.audio.currentTime = per * this.duration;
            }
        }"
        class="ghettoblaster-shell relative w-full bg-slate-900 border-2 border-slate-700 rounded-sm shadow-xl overflow-hidden font-mono group select-none hover:shadow-glow-md transition-shadow duration-300">
        
        <audio x-ref="audioEl" src="${safeSrc}" preload="metadata"></audio>

        <!-- Top Screw Header -->
        <div class="h-6 bg-slate-800 border-b border-slate-700 flex items-center justify-between px-2">
            <div class="flex gap-1">
                <div class="w-1.5 h-1.5 rounded-full bg-slate-600 shadow-inner"></div>
                <div class="w-1.5 h-1.5 rounded-full bg-slate-600 shadow-inner"></div>
            </div>
            <div class="text-[10px] text-slate-500 tracking-widest uppercase font-bold text-shadow-sm">Sonyk-9000</div>
            <div class="flex gap-1">
                <div class="w-1.5 h-1.5 rounded-full bg-slate-600 shadow-inner"></div>
                <div class="w-1.5 h-1.5 rounded-full bg-slate-600 shadow-inner"></div>
            </div>
        </div>

        <!-- Main Interface -->
        <div class="p-4 flex flex-col gap-4 relative bg-gradient-to-b from-slate-900 to-slate-950">
            
            <!-- LCD Display -->
            <div class="lcd-screen bg-[#1a2d28] border-2 border-slate-600 h-20 rounded-sm relative overflow-hidden flex flex-col justify-center px-4 shadow-[inset_0_0_20px_rgba(0,0,0,0.8)]">
                <!-- Scanlines -->
                <div class="absolute inset-0 bg-[linear-gradient(rgba(18,16,16,0)_50%,rgba(0,0,0,0.25)_50%),linear-gradient(90deg,rgba(255,0,0,0.06),rgba(0,255,0,0.02),rgba(0,0,255,0.06))] z-10 pointer-events-none bg-[length:100%_2px,3px_100%] opacity-20"></div>
                
                <div class="relative z-20 flex flex-col gap-1">
                    <div class="flex justify-between items-end border-b border-cyan-900/30 pb-1 mb-1">
                        <span class="${accent} text-[10px] tracking-wider animate-pulse font-bold" x-show="playing">PLAYING >></span>
                        <span class="text-slate-600 text-[10px] tracking-wider font-bold" x-show="!playing">STANDBY</span>
                        <span class="${accent} font-bold text-xs font-mono" x-text="new Date(progress * duration * 10 || 0).toISOString().substr(14, 5)">00:00</span>
                    </div>
                    <div class="text-cyan-300 font-bold text-sm truncate uppercase tracking-widest text-shadow-glow">${safeTitle}</div>
                    <div class="text-[9px] text-slate-500 uppercase">${label}</div>
                </div>

                <!-- Fake digital waveform -->
                <div class="absolute bottom-1 right-2 w-24 h-6 flex gap-0.5 items-end opacity-60">
                    <template x-for="i in 16">
                        <div class="flex-1 ${accentBg} shadow-[0_0_5px_rgba(34,211,238,0.5)] transition-all duration-100" 
                             :style="\`height: \${playing ? Math.random() * 100 : 10}%; opacity: \${playing ? 1 : 0.3}\`"></div>
                    </template>
                </div>
            </div>

            <!-- Controls Row -->
            <div class="flex items-center gap-4">
                <!-- Play Button -->
                <button @click="toggle()" 
                        class="w-14 h-14 bg-slate-800 rounded-full border-4 border-slate-950 active:border-slate-800 active:scale-95 transition-all ${accent} flex items-center justify-center hover:bg-slate-700 hover:shadow-[0_0_20px_rgba(34,211,238,0.2)] group/btn relative overflow-hidden">
                    <div class="absolute inset-0 bg-gradient-to-br from-white/5 to-transparent rounded-full pointer-events-none"></div>
                    <i class="ph-fill text-2xl drop-shadow-md" :class="playing ? 'ph-pause' : 'ph-play'"></i>
                </button>

                <!-- Scrubber -->
                <div class="flex-1 h-14 bg-slate-950 rounded border-2 border-slate-800 relative cursor-crosshair group/bar p-1 shadow-inner" @click="seek($event)">
                    <!-- Track Line -->
                    <div class="absolute top-1/2 left-3 right-3 h-1.5 bg-slate-800 -translate-y-1/2 rounded-full overflow-hidden pointer-events-none border border-slate-900">
                        <div class="h-full ${accentBg} ${accentShadow} transition-all duration-100 ease-linear" :style="\`width: \${progress}%\`"></div>
                    </div>
                    
                    <!-- Thumb -->
                    <div class="absolute top-1/2 w-3 h-8 bg-slate-300 border border-black -translate-y-1/2 -ml-1.5 transition-all duration-100 ease-linear pointer-events-none shadow-lg rounded-[1px] flex flex-col justify-center gap-[2px] items-center z-10" 
                         :style="\`left: calc(12px + (100% - 24px) * \${progress/100})\`">
                        <div class="w-2 h-[1px] bg-black/30"></div>
                        <div class="w-2 h-[1px] bg-black/30"></div>
                        <div class="w-2 h-[1px] bg-black/30"></div>
                    </div>
                </div>
                
                <!-- Knob Decor -->
                <div class="w-12 h-12 bg-slate-800 rounded-full border-b-4 border-slate-950 flex items-center justify-center relative transform rotate-45 shadow-xl">
                    <div class="w-1 h-4 bg-slate-950 absolute top-1.5 rounded-full shadow-[0_1px_0_rgba(255,255,255,0.1)]"></div>
                    <div class="absolute inset-0 rounded-full bg-gradient-to-br from-white/5 to-transparent pointer-events-none"></div>
                </div>
            </div>
        </div>
        
        <!-- Stickers / Badges -->
        <div class="absolute top-3 right-3 rotate-12 bg-yellow-400 text-black text-[9px] font-black px-1.5 py-0.5 border border-black shadow-sm uppercase z-10 opacity-90">${subLabel}</div>
    </div>
    `;
}
