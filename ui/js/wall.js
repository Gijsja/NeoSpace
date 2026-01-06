/**
 * Wall Stickers Logic
 * Handles drag-and-drop, persistence, and rendering of stickers.
 */

const STICKERS_PRESETS = ["🔥", "✨", "🎨", "💜", "🚀", "💻", "💾", "🌈", "👾", "⭐", "🎵", "🍕"];

class StickerManager {
    constructor(containerId, isHost, currentUserId, targetUserId) {
        this.container = document.getElementById(containerId);
        this.isHost = isHost;
        this.currentUserId = currentUserId;
        this.targetUserId = targetUserId;
        this.stickers = [];
        
        // Always init reception (guests can drop, hosts can drop)
        if (this.currentUserId) {
            this.initDragAndDrop();
        }
    }
    
    setStickers(stickersData) {
        this.stickers = stickersData || [];
        this.renderAll();
    }
    
    renderAll() {
        this.container.querySelectorAll('.sticker-item').forEach(el => el.remove());
        this.stickers.forEach(s => this.renderSticker(s));
    }
    
    renderSticker(data) {
        const el = document.createElement('div');
        el.className = 'sticker-item absolute select-none transition-transform drop-shadow-lg text-4xl';
        el.innerText = data.sticker_type;
        el.style.left = `${data.x_pos}px`;
        el.style.top = `${data.y_pos}px`;
        el.style.transform = `rotate(${data.rotation}deg) scale(${data.scale})`;
        el.style.zIndex = data.z_index || 10;
        el.dataset.id = data.id;
        
        // Tooltip
        if (data.placed_by_username) {
            el.title = `Placed by @${data.placed_by_username}`;
        }

        const isMySticker = this.currentUserId && (data.placed_by == this.currentUserId);
        
        if (this.isHost) {
            // Host can move everything
            el.draggable = true;
            el.style.cursor = 'grab';
            el.classList.add('hover:scale-110');
            el.addEventListener('dragstart', (e) => this.handleDragStart(e, data.id));
        } else {
             // Guests cannot move stickers once placed
             el.style.cursor = 'default';
        }

        // Deletion: Host can delete all. Guest can delete their own.
        if (this.isHost || isMySticker) {
            el.addEventListener('contextmenu', (e) => {
                e.preventDefault();
                if(confirm("Remove this sticker?")) {
                    this.deleteSticker(data.id);
                }
            });
            // Visual cue for deletable but not movable (for guests)
            if (!this.isHost && isMySticker) {
                el.style.cursor = 'context-menu';
                el.classList.add('hover:opacity-80');
            }
        }
        
        this.container.appendChild(el);
    }
    
    initDragAndDrop() {
        this.container.addEventListener('dragover', (e) => {
            e.preventDefault(); // Allow drop
        });
        
        this.container.addEventListener('drop', (e) => this.handleDrop(e));
    }
    
    handleDragStart(e, existingId) {
        // If existingId is present, we are moving an existing sticker
        if (existingId) {
            e.dataTransfer.setData('text/plain', JSON.stringify({
                type: 'move',
                id: existingId,
                offsetX: e.offsetX,
                offsetY: e.offsetY
            }));
        } else {
            // New sticker from palette
            const stickerChar = e.target.innerText;
            e.dataTransfer.setData('text/plain', JSON.stringify({
                type: 'new',
                sticker: stickerChar,
                offsetX: e.offsetX,
                offsetY: e.offsetY
            }));
        }
    }
    
    async handleDrop(e) {
        e.preventDefault();
        
        const rawData = e.dataTransfer.getData('text/plain');
        if (!rawData) return;
        
        try {
            const data = JSON.parse(rawData);
            const rect = this.container.getBoundingClientRect();
            
            // Calculate relative position in container
            const x = e.clientX - rect.left - (data.offsetX || 0);
            const y = e.clientY - rect.top - (data.offsetY || 0);
            
            if (data.type === 'new') {
                await this.createSticker(data.sticker, x, y);
            } else if (data.type === 'move' && this.isHost) {
                 // Only host can move existing stickers
                await this.moveSticker(data.id, x, y);
            }
        } catch (err) {
            console.error(err);
        }
    }
    
    async createSticker(char, x, y) {
        // Optimistic update
        const tempId = 'temp-' + Date.now();
        const newSticker = {
            id: tempId,
            sticker_type: char,
            x_pos: x,
            y_pos: y,
            rotation: (Math.random() * 40 - 20).toFixed(0),
            scale: 1,
            z_index: 10,
            placed_by: this.currentUserId,
            placed_by_username: 'You' // temporary
        };
        
        this.stickers.push(newSticker);
        this.renderSticker(newSticker);
        
        try {
            const res = await fetch('/profile/sticker/add', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    sticker_type: char,
                    x: x,
                    y: y,
                    target_user_id: this.targetUserId
                })
            });
            const resData = await res.json();
            
            if (resData.ok) {
                // Update ID
                const idx = this.stickers.findIndex(s => s.id === tempId);
                if (idx !== -1) {
                    this.stickers[idx].id = resData.id;
                    this.stickers[idx].placed_by_username = resData.placed_by_username;
                    this.renderAll(); 
                }
            } else {
                console.error("Failed to save sticker");
            }
        } catch (err) {
            console.error(err);
        }
    }
    
    async moveSticker(id, x, y) {
        // Optimistic
        const s = this.stickers.find(st => st.id == id);
        if (s) {
            s.x_pos = x;
            s.y_pos = y;
            this.renderAll();
            
            await fetch('/profile/sticker/update', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    id: id,
                    x: x,
                    y: y
                })
            });
        }
    }
    
    async deleteSticker(id) {
        // Optimistic
        this.stickers = this.stickers.filter(s => s.id != id);
        this.renderAll();
        
        await fetch('/profile/sticker/remove', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ id: id })
        });
    }
}

// Global Exports
window.StickerManager = StickerManager;
window.STICKERS_PRESETS = STICKERS_PRESETS;
