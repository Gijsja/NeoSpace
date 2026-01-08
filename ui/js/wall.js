/**
 * Wall Stickers Logic
 * Handles drag-and-drop, persistence, and rendering of stickers.
 */

if (!window.StickerManager) {
    const STICKERS_PRESETS = ["🔥", "✨", "🎨", "💜", "🚀", "💻", "💾", "🌈", "👾", "⭐", "🎵", "🍕"];

    window.StickerManager = class StickerManager {
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
            if (!this.container) return;
            this.container.querySelectorAll('.sticker-item').forEach(el => el.remove());
            this.stickers.forEach(s => this.renderSticker(s));
        }
        
        renderSticker(data) {
            const el = document.createElement('div');
            el.className = 'sticker-item absolute select-none transition-transform drop-shadow-lg';
            
            // Sprint 11: Render Image or Emoji
            if (data.image_path) {
                // Image Sticker
                const img = document.createElement('img');
                img.src = data.image_path;
                img.className = 'max-w-[150px] max-h-[150px] object-contain pointer-events-none rounded border-2 border-white/20 shadow-xl';
                el.appendChild(img);
            } else {
                // Emoji Sticker
                el.innerText = data.sticker_type;
                el.className += ' text-4xl';
            }
            
            el.style.left = `${data.x_pos}px`;
            el.style.top = `${data.y_pos}px`;
            el.style.transform = `rotate(${data.rotation || 0}deg) scale(${data.scale || 1})`;
            
            // Add interaction only if host
            if (this.isHost) {
                this.makeInteractable(el, data.id);
            }
            
            this.container.appendChild(el);
        }
        
        initDragAndDrop() {
            if (!this.container) return;
            
            this.container.addEventListener('dragover', (e) => {
                e.preventDefault();
                e.dataTransfer.dropEffect = 'copy';
            });
            
            this.container.addEventListener('drop', (e) => {
                e.preventDefault();
                const x = e.offsetX;
                const y = e.offsetY;
                
                // Check if file drop or emoji drop
                // This logic is mostly handled in wall_ui.js for files, but here for positioning?
                // Actually wall_ui.js handles the 'drop' event on the CONTAINER usually
                // Let's see if this conflicts. 
                // The original code probably had drop logic here or wall_ui.js?
                // Assuming wall_ui.js handles file uploads.
            });
        }
        
        makeInteractable(el, id) {
             let isDragging = false;
             let startX, startY;
             
             el.addEventListener('mousedown', (e) => {
                 if (e.button !== 0) return; // Only left click
                 isDragging = true;
                 startX = e.offsetX;
                 startY = e.offsetY;
                 el.style.cursor = 'grabbing';
             });
             
             window.addEventListener('mouseup', () => {
                 if (isDragging) {
                     isDragging = false;
                     el.style.cursor = 'default';
                     this.saveStickerState(id, el);
                 }
             });
             
             window.addEventListener('mousemove', (e) => {
                 if (!isDragging) return;
                 const rect = this.container.getBoundingClientRect();
                 const x = e.clientX - rect.left - startX;
                 const y = e.clientY - rect.top - startY;
                 
                 el.style.left = `${x}px`;
                 el.style.top = `${y}px`;
             });
             
             el.addEventListener('contextmenu', (e) => {
                 e.preventDefault();
                 if (confirm('Delete sticker?')) {
                     this.deleteSticker(id, el);
                 }
             });
        }
        
        saveStickerState(id, el) {
            const x = parseInt(el.style.left);
            const y = parseInt(el.style.top);
            
            // Optimistic update
            const sticker = this.stickers.find(s => s.id === id);
            if (sticker) {
                sticker.x_pos = x;
                sticker.y_pos = y;
            }
            
            fetch('/wall/sticker/move', {
                method: 'POST',
                headers: {
                     'Content-Type': 'application/json',
                     'X-CSRFToken': document.querySelector('meta[name="csrf-token"]').content
                },
                body: JSON.stringify({ id, x_pos: x, y_pos: y })
            });
        }
        
        deleteSticker(id, el) {
            el.remove();
            this.stickers = this.stickers.filter(s => s.id !== id);
            
            fetch('/wall/sticker/delete', {
                method: 'POST',
                headers: {
                     'Content-Type': 'application/json',
                     'X-CSRFToken': document.querySelector('meta[name="csrf-token"]').content
                },
                body: JSON.stringify({ id })
            });
        }
    };
}
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
        
        // 1. Check for Files (Sprint 11: Image Collage)
        if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
            const file = e.dataTransfer.files[0];
            if (file.type.startsWith('image/')) {
                const rect = this.container.getBoundingClientRect();
                const x = e.clientX - rect.left;
                const y = e.clientY - rect.top;
                await this.uploadImageSticker(file, x, y);
            }
            return;
        }

        // 2. Handling existing dragged stickers or text
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
    
    async uploadImageSticker(file, x, y) {
        // Optimistic Preview
        const tempId = 'temp-img-' + Date.now();
        const reader = new FileReader();
        
        reader.onload = (e) => {
            const newSticker = {
                id: tempId,
                sticker_type: 'image',
                image_path: e.target.result, // Data URL for preview
                x_pos: x - 50, // Center it roughly
                y_pos: y - 50,
                rotation: (Math.random() * 20 - 10).toFixed(0),
                scale: 1,
                z_index: 20,
                placed_by: this.currentUserId,
                placed_by_username: 'You'
            };
            this.stickers.push(newSticker);
            this.renderSticker(newSticker);
        };
        reader.readAsDataURL(file);

        // Upload
        const formData = new FormData();
        formData.append('image', file);
        formData.append('x', x - 50);
        formData.append('y', y - 50);
        formData.append('target_user_id', this.targetUserId);

        try {
            const res = await fetch('/profile/sticker/add', {
                method: 'POST',
                body: formData // No headers, browser sets multipart
            });
            const resData = await res.json();
            
            if (resData.ok) {
                 // Update ID and real path
                const idx = this.stickers.findIndex(s => s.id === tempId);
                if (idx !== -1) {
                    this.stickers[idx].id = resData.id;
                    this.stickers[idx].image_path = resData.image_path;
                    this.stickers[idx].placed_by_username = resData.placed_by_username;
                    // Don't re-render immediately to avoid flash, but next load handles it
                }
            } else {
                 console.error("Upload failed", resData.error);
                 alert("Failed to upload image: " + resData.error);
                 // Cleanup
                 this.stickers = this.stickers.filter(s => s.id !== tempId);
                 this.renderAll();
            }
        } catch(e) {
            console.error("Upload error", e);
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
