/**
 * WallStickers.js
 * Handles the "Guestbook Collage" feature: Drag & Drop stickers, positioning, and saving.
 */
export default class WallStickers {
    constructor(canvasId) {
        this.canvas = document.getElementById(canvasId);
        this.profileId = null;
        this.isOwner = false;

        // State
        this.activeSticker = null;
        this.stickers = [];

        this.init();
    }

    init() {
        if (!this.canvas) return;

        // Drop Zone events
        this.canvas.addEventListener('dragover', (e) => this.handleDragOver(e));
        this.canvas.addEventListener('dragleave', (e) => this.handleDragLeave(e));
        this.canvas.addEventListener('drop', (e) => this.handleDrop(e));

        // Global click to deselect
        document.addEventListener('click', (e) => {
            if (!e.target.closest('.sticker-item')) {
                this.deselectAll();
            }
        });
    }

    setProfile(profileId, isOwner) {
        this.profileId = profileId;
        this.isOwner = isOwner; // In future, maybe check if user is allowed to post
    }

    load(stickers) {
        // Clear canvas (except static elements if any, though here we clear all injected stickers)
        const existing = this.canvas.querySelectorAll('.sticker-item');
        existing.forEach(el => el.remove());

        this.stickers = stickers || [];
        this.stickers.forEach(s => this.renderSticker(s));
    }

    renderSticker(data) {
        const el = document.createElement('div');
        el.className = 'sticker-item absolute cursor-grab hover:z-50 transition-transform active:cursor-grabbing';
        el.dataset.id = data.id;

        // Styles
        el.style.left = `${data.x_pos}%`;
        el.style.top = `${data.y_pos}%`;
        el.style.zIndex = data.z_index || 10;
        el.style.transform = `rotate(${data.rotation || 0}deg) scale(${data.scale || 1})`;

        // Image
        const img = document.createElement('img');
        img.src = data.image_path;
        img.className = 'max-w-[150px] max-h-[150px] object-contain drop-shadow-md pointer-events-none select-none';

        // Controls (Delete) - Only show if owner or author (checked in render)
        // For simplicity, we create them but hide via CSS unless active/hover
        const deleteBtn = document.createElement('button');
        deleteBtn.innerHTML = '<i class="ph-bold ph-x"></i>';
        deleteBtn.className = 'absolute -top-2 -right-2 w-6 h-6 bg-red-500 text-white rounded-full flex items-center justify-center text-xs opacity-0 group-hover:opacity-100 transition shadow-sm z-20';
        deleteBtn.onclick = (e) => {
            e.stopPropagation();
            this.deleteSticker(data.id, el);
        };

        el.appendChild(img);
        el.appendChild(deleteBtn);

        // Make draggable
        this.makeDraggable(el);

        // Add to canvas
        this.canvas.appendChild(el);
    }

    makeDraggable(el) {
        let isDragging = false;
        let startX, startY, initialLeft, initialTop;

        el.addEventListener('mousedown', (e) => {
            if (e.button !== 0) return; // Only left click
            e.stopPropagation();

            isDragging = true;
            this.activeSticker = el;

            // Bring to front
            el.style.zIndex = 50;

            startX = e.clientX;
            startY = e.clientY;

            // Percentage based positioning
            const rect = this.canvas.getBoundingClientRect();
            initialLeft = parseFloat(el.style.left); // % value
            initialTop = parseFloat(el.style.top);   // % value

            el.classList.add('cursor-grabbing');
            el.classList.add('scale-105');
        });

        window.addEventListener('mousemove', (e) => {
            if (!isDragging) return;
            e.preventDefault();

            const rect = this.canvas.getBoundingClientRect();
            const dx = e.clientX - startX;
            const dy = e.clientY - startY;

            // Convert delta px to %
            const dxPercent = (dx / rect.width) * 100;
            const dyPercent = (dy / rect.height) * 100;

            let newLeft = initialLeft + dxPercent;
            let newTop = initialTop + dyPercent;

            // Constraints (keep roughly inside 0-100)
            // Allow slight overflow for aesthetic "messiness" (-5 to 105)
            // newLeft = Math.max(-10, Math.min(100, newLeft));
            // newTop = Math.max(-10, Math.min(100, newTop));

            el.style.left = `${newLeft}%`;
            el.style.top = `${newTop}%`;
        });

        window.addEventListener('mouseup', (e) => {
            if (!isDragging) return;
            isDragging = false;
            el.classList.remove('cursor-grabbing');
            el.classList.remove('scale-105');
            el.style.zIndex = el.dataset.z_index || 10; // Reset Z or keep high? 
            // Better to update z-index in DB to be top? For now, reset to avoid z-fighting.

            // Save Position
            const finalLeft = parseFloat(el.style.left);
            const finalTop = parseFloat(el.style.top);
            this.saveStickerPosition(el.dataset.id, finalLeft, finalTop);
        });
    }

    handleDragOver(e) {
        e.preventDefault();
        this.canvas.classList.add('bg-blue-50', 'border-blue-500');
    }

    handleDragLeave(e) {
        e.preventDefault();
        this.canvas.classList.remove('bg-blue-50', 'border-blue-500');
    }

    handleDrop(e) {
        e.preventDefault();
        this.canvas.classList.remove('bg-blue-50', 'border-blue-500');

        if (!this.profileId) {
            alert("Profile not loaded.");
            return;
        }

        const files = e.dataTransfer.files;
        if (files.length > 0) {
            const file = files[0];
            if (!file.type.startsWith('image/')) {
                alert("Only images are allowed!");
                return;
            }

            // Calculate drop position in %
            const rect = this.canvas.getBoundingClientRect();
            const x = ((e.clientX - rect.left) / rect.width) * 100;
            const y = ((e.clientY - rect.top) / rect.height) * 100;

            this.uploadSticker(file, x, y);
        }
    }

    async uploadSticker(file, x, y) {
        const formData = new FormData();
        formData.append('image', file);
        formData.append('profile_id', this.profileId);
        formData.append('x_pos', x);
        formData.append('y_pos', y);

        // Optimistic UI? Maybe wait for server for ID.
        // Showing a spinner or temp placeholder could be good.

        try {
            const res = await fetch('/wall/sticker/add', {
                method: 'POST',
                body: formData
            });
            const data = await res.json();

            if (data.success) {
                this.renderSticker(data.sticker);
            } else {
                alert(data.error || "Upload failed");
            }
        } catch (err) {
            console.error(err);
            alert("Connection error");
        }
    }

    async saveStickerPosition(id, x, y) {
        try {
            await fetch('/wall/sticker/update', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ id, x: x, y: y })
            });
        } catch (err) {
            console.error("Failed to save position", err);
        }
    }

    async deleteSticker(id, el) {
        if (!confirm("Remove this sticker?")) return;

        try {
            const res = await fetch('/wall/sticker/delete', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ id })
            });
            if (res.ok) {
                el.remove();
            }
        } catch (err) {
            console.error(err);
        }
    }

    deselectAll() {
        // remove active states if any
    }
}
