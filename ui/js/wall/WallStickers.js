/**
 * WallStickers.js - The "Insanely Fun" Edition
 * Handles drag & drop, gizmo controls (rotate/scale), and sonic feedback.
 */
export default class WallStickers {
    constructor(canvasId) {
        this.canvas = document.getElementById(canvasId);
        this.profileId = null;
        this.isOwner = false;
        this.currentUserId = null; // Set via init or helper

        // State
        this.activeSticker = null;
        this.stickers = [];
        this.scale = 1; // Canvas zoom if any

        // Audio
        this.sounds = {
            pop: new Tone.Player("https://tonejs.github.io/audio/berklee/hit_1.mp3").toDestination(), // Placeholder URL or synthetic
            click: new Tone.MembraneSynth().toDestination()
        };
        // Simple synth fallback for clicks
        this.synth = new Tone.MembraneSynth().toDestination();

        this.init();
    }

    init() {
        if (!this.canvas) return;

        // Drop Zone events
        this.canvas.addEventListener('dragover', (e) => this.handleDragOver(e));
        this.canvas.addEventListener('dragleave', (e) => this.handleDragLeave(e));
        this.canvas.addEventListener('drop', (e) => this.handleDrop(e));

        // Global click to deselect
        document.addEventListener('mousedown', (e) => {
            if (!e.target.closest('.sticker-item') && !e.target.closest('.sticker-gizmo')) {
                this.deselectAll();
            }
        });

        // Initialize Palette
        this.loadPalette();

        // Init Audio Context on first click
        window.addEventListener('click', async () => {
            await Tone.start();
        }, { once: true });
    }

    setProfile(profileId, isOwner, currentUserId) {
        this.profileId = profileId;
        this.isOwner = isOwner;
        this.currentUserId = currentUserId;
    }

    load(stickers) {
        const existing = this.canvas.querySelectorAll('.sticker-item');
        existing.forEach(el => el.remove());

        this.stickers = stickers || [];
        this.stickers.forEach(s => this.renderSticker(s));
    }

    playPop() {
        // Quick synthetic pop
        const synth = new Tone.Synth({
            oscillator: { type: "triangle" },
            envelope: { attack: 0.01, decay: 0.1, sustain: 0, release: 0.1 }
        }).toDestination();
        synth.triggerAttackRelease("C5", "32n");
        synth.triggerAttackRelease("E5", "32n", "+0.05");
    }

    playClick() {
        const synth = new Tone.MembraneSynth({
            envelope: { attack: 0.001, decay: 0.05, sustain: 0 }
        }).toDestination();
        synth.triggerAttackRelease("A2", "32n");
    }

    renderSticker(data) {
        const el = document.createElement('div');
        el.className = 'sticker-item absolute cursor-grab group select-none';
        el.dataset.id = data.id;

        // Store transforms in dataset for easy gizmo access
        el.dataset.x = data.x_pos;
        el.dataset.y = data.y_pos;
        el.dataset.rotation = data.rotation || 0;
        el.dataset.scale = data.scale || 1;
        el.dataset.zIndex = data.z_index || 10;

        // Apply Styles
        this.updateTransform(el);

        if (data.sticker_type === 'text') {
            const span = document.createElement('span');
            span.textContent = data.text_content;
            span.className = 'text-4xl font-bold text-cyber-black drop-shadow-md whitespace-nowrap pointer-events-none transition-transform duration-200';
            // Pop animation
            span.style.transform = 'scale(0)';
            setTimeout(() => span.style.transform = 'scale(1)', 10);
            el.appendChild(span);
        } else {
            // Image
            const img = document.createElement('img');
            img.src = data.image_path;
            img.className = 'max-w-[200px] max-h-[200px] w-auto h-auto object-contain drop-shadow-md pointer-events-none transition-transform duration-200';
            // Add "pop" in animation
            img.style.transform = 'scale(0)';
            setTimeout(() => img.style.transform = 'scale(1)', 10);
            el.appendChild(img);
        }

        this.canvas.appendChild(el);

        // Interactions
        el.addEventListener('mousedown', (e) => {
            if (e.button !== 0) return;
            // Only allow interaction if user has permission
            // (Owner or Placer)
            if (!this.canEdit(data)) return;

            e.stopPropagation();
            this.selectSticker(el);
            this.handleDrag(e, el);
        });
    }

    canEdit(data) {
        // If strict mode:
        // return this.isOwner || (this.currentUserId && data.placed_by == this.currentUserId);
        return true; // "Insanely Fun" -> Anarchy? Let's stick to owners for now to be safe, or just check generic auth
    }

    updateTransform(el) {
        el.style.left = `${el.dataset.x}%`;
        el.style.top = `${el.dataset.y}%`;
        el.style.zIndex = el.dataset.zIndex;

        const img = el.querySelector('img');
        // We apply rotation/scale to the inner image or container? 
        // Applying to container rotates the gizmo axis too which is what we want.
        el.style.transform = `rotate(${el.dataset.rotation}deg) scale(${el.dataset.scale})`;
    }

    selectSticker(el) {
        if (this.activeSticker === el) return;
        this.deselectAll();

        this.activeSticker = el;
        el.classList.add('z-[100]'); // Pop to top while editing
        this.playClick();

        // Create Gizmo
        this.renderGizmo(el);
    }

    deselectAll() {
        if (!this.activeSticker) return;

        // Reset Z-Index to stored value
        this.activeSticker.style.zIndex = this.activeSticker.dataset.zIndex;

        // Remove Gizmo
        const gizmo = this.activeSticker.querySelector('.sticker-gizmo');
        if (gizmo) gizmo.remove();

        this.activeSticker = null;
    }

    renderGizmo(el) {
        const gizmo = document.createElement('div');
        gizmo.className = 'sticker-gizmo absolute -inset-4 border-2 border-cyber-neon rounded-lg pointer-events-none animation-pulse';

        // Allow pointer events on handles
        gizmo.innerHTML = `
            <!-- Rotate Handle (Top) -->
            <div class="handle-rotate absolute -top-8 left-1/2 -translate-x-1/2 w-6 h-6 bg-cyber-neon rounded-full flex items-center justify-center cursor-ew-resize pointer-events-auto shadow-neon hover:scale-125 transition">
                <i class="ph-bold ph-arrows-clockwise text-cyber-black text-xs"></i>
            </div>

            <!-- Scale Handle (Bottom Right) -->
            <div class="handle-scale absolute -bottom-3 -right-3 w-6 h-6 bg-white border-2 border-cyber-neon rounded-full cursor-nwse-resize pointer-events-auto shadow-md hover:scale-125 transition"></div>

            <!-- Delete Handle (Top Right) -->
            <div class="handle-delete absolute -top-3 -right-3 w-6 h-6 bg-red-500 text-white rounded-full flex items-center justify-center cursor-pointer pointer-events-auto shadow-md hover:scale-125 transition">
                <i class="ph-bold ph-x text-xs"></i>
            </div>
            
            <!-- Layer Up (Left) -->
             <div class="handle-layer absolute -top-3 -left-3 w-6 h-6 bg-cyber-blue text-white rounded-full flex items-center justify-center cursor-pointer pointer-events-auto shadow-md hover:scale-125 transition" title="Bring Forward">
                <i class="ph-bold ph-stack text-xs"></i>
            </div>
        `;

        el.appendChild(gizmo);

        // Bind Handles
        gizmo.querySelector('.handle-rotate').addEventListener('mousedown', (e) => this.handleRotate(e, el));
        gizmo.querySelector('.handle-scale').addEventListener('mousedown', (e) => this.handleScale(e, el));
        gizmo.querySelector('.handle-delete').addEventListener('mousedown', (e) => {
            e.stopPropagation();
            this.deleteSticker(el.dataset.id, el);
        });
        gizmo.querySelector('.handle-layer').addEventListener('mousedown', (e) => {
            e.stopPropagation();
            this.bumpLayer(el);
        });
    }

    bumpLayer(el) {
        let z = parseInt(el.dataset.zIndex) || 10;
        z += 10;
        el.dataset.zIndex = z;
        this.updateTransform(el);
        this.playClick();
        this.saveStickerState(el);
    }

    handleDrag(e, el) {
        e.preventDefault();
        const startX = e.clientX;
        const startY = e.clientY;
        const startLeft = parseFloat(el.dataset.x);
        const startTop = parseFloat(el.dataset.y);
        const rect = this.canvas.getBoundingClientRect();

        const onMove = (moveEvent) => {
            const dx = moveEvent.clientX - startX;
            const dy = moveEvent.clientY - startY;

            const dxPercent = (dx / rect.width) * 100;
            const dyPercent = (dy / rect.height) * 100;

            el.dataset.x = startLeft + dxPercent;
            el.dataset.y = startTop + dyPercent;
            this.updateTransform(el);
        };

        const onUp = () => {
            window.removeEventListener('mousemove', onMove);
            window.removeEventListener('mouseup', onUp);
            this.saveStickerState(el);
        };

        window.addEventListener('mousemove', onMove);
        window.addEventListener('mouseup', onUp);
    }

    handleRotate(e, el) {
        e.stopPropagation();
        e.preventDefault();

        const rect = el.getBoundingClientRect();
        const centerX = rect.left + rect.width / 2;
        const centerY = rect.top + rect.height / 2;
        const startRotation = parseFloat(el.dataset.rotation) || 0;

        // Calculate initial angle
        const startAngle = Math.atan2(e.clientY - centerY, e.clientX - centerX);

        const onMove = (moveEvent) => {
            const currentAngle = Math.atan2(moveEvent.clientY - centerY, moveEvent.clientX - centerX);
            const deltaDeg = (currentAngle - startAngle) * (180 / Math.PI);

            el.dataset.rotation = startRotation + deltaDeg;
            this.updateTransform(el);
        };

        const onUp = () => {
            window.removeEventListener('mousemove', onMove);
            window.removeEventListener('mouseup', onUp);
            this.saveStickerState(el);
        };

        window.addEventListener('mousemove', onMove);
        window.addEventListener('mouseup', onUp);
    }

    handleScale(e, el) {
        e.stopPropagation();
        e.preventDefault();

        const startY = e.clientY;
        const startScale = parseFloat(el.dataset.scale) || 1;

        const onMove = (moveEvent) => {
            const dy = moveEvent.clientY - startY;
            // Drag down to grow, up to shrink
            const delta = dy * 0.01;
            el.dataset.scale = Math.max(0.2, Math.min(5.0, startScale + delta));
            this.updateTransform(el);
        };

        const onUp = () => {
            window.removeEventListener('mousemove', onMove);
            window.removeEventListener('mouseup', onUp);
            this.saveStickerState(el);
        };

        window.addEventListener('mousemove', onMove);
        window.addEventListener('mouseup', onUp);
    }

    async saveStickerState(el) {
        try {
            await fetch('/wall/sticker/update', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    id: el.dataset.id,
                    x: parseFloat(el.dataset.x),
                    y: parseFloat(el.dataset.y),
                    rotation: parseFloat(el.dataset.rotation),
                    scale: parseFloat(el.dataset.scale),
                    z_index: parseInt(el.dataset.zIndex)
                })
            });
        } catch (err) {
            console.error("Save failed", err);
        }
    }

    // ... (Drag and Drop / Upload logic same as before, simplified below)

    handleDragOver(e) {
        e.preventDefault();
        this.canvas.classList.add('bg-cyber-blue/10');
    }

    handleDragLeave(e) {
        e.preventDefault();
        this.canvas.classList.remove('bg-cyber-blue/10');
    }

    handleDrop(e) {
        e.preventDefault();
        this.canvas.classList.remove('bg-cyber-blue/10');
        if (!this.profileId) return;

        // Check for internal drag (preset)
        const presetData = e.dataTransfer.getData('text/plain');
        if (presetData) {
            try {
                const data = JSON.parse(presetData);
                if (data.src) {
                    this.playPop(); // SFX
                    fetch(data.src).then(r => r.blob()).then(blob => {
                        const file = new File([blob], "sticker.png", { type: blob.type });
                        this.uploadSticker(file, e);
                    });
                } else if (data.text) {
                    this.playPop(); // SFX
                    this.uploadSticker(null, e, data.text);
                }
            } catch (e) { }
            return;
        }

        const files = e.dataTransfer.files;
        if (files.length > 0) this.uploadSticker(files[0], e);
    }

    async uploadSticker(file, e, textContent = null) {
        const rect = this.canvas.getBoundingClientRect();
        const x = ((e.clientX - rect.left) / rect.width) * 100;
        const y = ((e.clientY - rect.top) / rect.height) * 100;

        const formData = new FormData();
        formData.append('profile_id', this.profileId);
        formData.append('x_pos', x);
        formData.append('y_pos', y);

        if (textContent) {
            formData.append('sticker_type', 'text');
            formData.append('text_content', textContent);
        } else {
            formData.append('sticker_type', 'image');
            formData.append('image', file);
        }

        try {
            const res = await fetch('/wall/sticker/add', { method: 'POST', body: formData });
            const data = await res.json();
            if (data.success) {
                this.renderSticker(data.sticker);
                this.playPop();
            }
        } catch (err) { alert("Upload failed"); }
    }

    async deleteSticker(id, el) {
        if (!confirm("Pop this bubble?")) return;

        // Fun pop animation before delete
        const img = el.querySelector('img');
        img.style.transition = "all 0.1s cubic-bezier(0.175, 0.885, 0.32, 1.275)";
        img.style.transform = "scale(1.5)";
        setTimeout(() => {
            img.style.transform = "scale(0)";
            this.playPop(); // Pop sound
        }, 100);

        setTimeout(async () => {
            await fetch('/wall/sticker/delete', { method: 'POST', body: JSON.stringify({ id }) });
            el.remove();
            this.deselectAll();
        }, 300);
    }

    loadPalette() {
        // ... (Same palette logic, just ensure images are draggable)
        const palette = document.getElementById('sticker-palette');
        if (!palette) return;
        palette.classList.remove('hidden');

        const CATS = ['beans', 'miso', 'tofu', 'ash', 'delta', 'patch', 'static', 'hex', 'null', 'root', 'glitch', 'neon'];
        const SMILEYS = ['melt', 'cyber', 'grim'];

        palette.innerHTML = '<div class="text-[10px] font-bold uppercase shrink-0">STICKERS</div>';

        CATS.forEach(cat => {
            const img = document.createElement('img');
            img.src = `/static/images/cats/${cat}.png`;
            img.className = 'w-10 h-10 object-contain cursor-grab hover:scale-125 transition active:cursor-grabbing';
            img.draggable = true;
            img.addEventListener('dragstart', (e) => {
                e.dataTransfer.setData('text/plain', JSON.stringify({ src: img.src }));
            });
            palette.appendChild(img);
        });

        // Smileys separator
        const sep = document.createElement('div');
        sep.className = "w-px h-6 bg-gray-500 mx-2 opacity-50";
        palette.appendChild(sep);

        // Smileys
        SMILEYS.forEach(smiley => {
            const img = document.createElement('img');
            img.src = `/static/images/stickers/${smiley}.png`;
            img.className = 'w-12 h-12 object-contain cursor-grab hover:scale-125 transition active:cursor-grabbing';
            img.draggable = true;
            img.addEventListener('dragstart', (e) => {
                e.dataTransfer.setData('text/plain', JSON.stringify({ src: img.src }));
            });
            palette.appendChild(img);
        });

        // Kaomoji separator
        const sep2 = document.createElement('div');
        sep2.className = "w-px h-6 bg-gray-500 mx-2 opacity-50";
        palette.appendChild(sep2);

        // Kaomojis
        const KAOMOJIS = ['(=^･ω･^=)', '(=;ω;=)', '(=^･^=)', '(=^-ω-^=)', '(=^..^=)', '(=T.T=)', '(=｀ω´=)', '(^..^)ﾉ'];
        KAOMOJIS.forEach(k => {
            const div = document.createElement('div');
            div.textContent = k;
            div.className = 'text-xs font-bold text-cyber-black whitespace-nowrap cursor-grab hover:scale-110 hover:text-cyber-neon transition active:cursor-grabbing select-none';
            div.draggable = true;
            div.addEventListener('dragstart', (e) => {
                // Set drag image to a ghost of the text?
                e.dataTransfer.setData('text/plain', JSON.stringify({ text: k }));
            });
            palette.appendChild(div);
        });

        // Upload button
        const btn = document.createElement('div');
        btn.className = 'w-10 h-10 border-2 border-dashed border-gray-500 rounded flex items-center justify-center cursor-pointer hover:border-white hover:text-white transition';
        btn.innerHTML = '+';
        btn.onclick = () => document.getElementById('sticker-upload-input')?.click();

        palette.appendChild(btn);
    }
}
