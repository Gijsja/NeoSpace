
/**
 * IsoGrid.js
 * Handles Isometric Hexgrid math and rendering.
 */

export class IsoGrid {
    constructor(ctx, config) {
        this.ctx = ctx;
        this.cols = config.cols || 20;
        this.rows = config.rows || 20;
        this.tileWidth = config.tileWidth || 64; // Horizontal width of a tile
        this.tileHeight = config.tileHeight || 32; // Vertical height of a tile
        this.originX = config.originX || 400; // Screen X for grid(0,0)
        this.originY = config.originY || 100; // Screen Y for grid(0,0)

        // Assets
        this.assets = {
            tile: null, // Image or null (draw procedurally if null)
            cats: {}    // Map of cat names to ID
        };

        this.entities = []; // { x, y, type, id, data }
    }

    /**
     * Prescale assets to optimized size (e.g. 64px) to avoid realtime scaling.
     */
    bakeAssets(images) {
        // Create an offscreen canvas for each image
        const baked = {};
        for (const [key, img] of Object.entries(images)) {
            const size = this.tileWidth; // Target size
            const canvas = document.createElement('canvas');
            canvas.width = size;
            canvas.height = size;
            const ctx = canvas.getContext('2d');
            // Draw scaled down
            ctx.drawImage(img, 0, 0, size, size);
            baked[key] = canvas;
        }
        this.assets.cats = baked;
    }

    /**
     * Converts Grid coordinates to Screen coordinates.
     * Isometric projection:
     * x' = (x - y) * (width / 2)
     * y' = (x + y) * (height / 2)
     */
    toScreen(col, row) {
        const x = (col - row) * (this.tileWidth / 2) + this.originX;
        const y = (col + row) * (this.tileHeight / 2) + this.originY;
        return { x, y };
    }

    /**
     * Primitive Click detection (Hit testing)
     * Reverse projection approximation
     */
    fromScreen(screenX, screenY) {
        // Adjust for origin
        const adjX = screenX - this.originX;
        const adjY = screenY - this.originY;

        // Solve system of equations
        // adjX = (col - row) * w/2
        // adjY = (col + row) * h/2

        // col - row = adjX / (w/2)
        // col + row = adjY / (h/2)

        const w2 = this.tileWidth / 2;
        const h2 = this.tileHeight / 2;

        const col = Math.round((adjX / w2 + adjY / h2) / 2);
        const row = Math.round((adjY / h2 - adjX / w2) / 2);

        return { col, row };
    }

    addEntity(entity) {
        // entity: { id, x, y, type, meta }
        // Update existing if ID matches
        const idx = this.entities.findIndex(e => e.id === entity.id);
        if (idx >= 0) {
            // Smooth lerp would go here, for now just snap
            // We can add a targetX/targetY and lerp in update()
            const existing = this.entities[idx];
            existing.targetX = entity.x;
            existing.targetY = entity.y;
            // Immediate snap for now implies no lerp logic implemented yet
            // logic is handled in render loop
        } else {
            this.entities.push({
                ...entity,
                curX: entity.x,
                curY: entity.y,
                targetX: entity.x,
                targetY: entity.y
            });
        }
    }

    removeEntity(id) {
        this.entities = this.entities.filter(e => e.id !== id);
    }

    update() {
        // Interpolate positions
        for (const ent of this.entities) {
            const dx = ent.targetX - ent.curX;
            const dy = ent.targetY - ent.curY;

            if (Math.abs(dx) > 0.01 || Math.abs(dy) > 0.01) {
                ent.curX += dx * 0.1;
                ent.curY += dy * 0.1;
            } else {
                ent.curX = ent.targetX;
                ent.curY = ent.targetY;
            }
        }
    }

    draw() {
        // 1. Draw Floor
        this.drawFloor();

        // 2. Draw Entities (Z-Sorted)
        // Sort by row + col (or just screen Y)
        // Isometric depth sort: (x + y) usually works, or screen Y
        this.entities.sort((a, b) => {
            const screenA = this.toScreen(a.curX, a.curY);
            const screenB = this.toScreen(b.curX, b.curY);
            return screenA.y - screenB.y;
        });

        for (const ent of this.entities) {
            this.drawEntity(ent);
        }
    }

    drawFloor() {
        const { ctx, cols, rows, tileWidth, tileHeight } = this;

        for (let r = 0; r < rows; r++) {
            for (let c = 0; c < cols; c++) {
                const pos = this.toScreen(c, r);

                // Draw Tile (Diamond)
                ctx.beginPath();
                ctx.moveTo(pos.x, pos.y); // Top
                ctx.lineTo(pos.x + tileWidth / 2, pos.y + tileHeight / 2); // Right
                ctx.lineTo(pos.x, pos.y + tileHeight); // Bottom
                ctx.lineTo(pos.x - tileWidth / 2, pos.y + tileHeight / 2); // Left
                ctx.closePath();

                // Style
                ctx.fillStyle = (c + r) % 2 === 0 ? '#222' : '#333'; // Checkered
                ctx.fill();

                // Highlight edges
                ctx.strokeStyle = '#444';
                ctx.lineWidth = 1;
                ctx.stroke();

                // Highlight grid borders
                // ctx.strokeStyle = 'cyan';
                // ctx.stroke();
            }
        }
    }

    drawEntity(ent) {
        const pos = this.toScreen(ent.curX, ent.curY);
        const img = this.assets.cats[ent.meta.avatar] || this.assets.cats['default'];

        if (img) {
            // Draw Image Billboard
            // Use baked size (tileWidth) directly, no scaling needed
            const w = this.tileWidth;
            const h = this.tileHeight * 2; // Assuming square asset baked to tileWidth, but let's keep aspect ratio logic or just use w/h from canvas

            // Actually, baked assets are square (size x size)
            // We want to draw them centered at bottom

            this.ctx.drawImage(
                img,
                pos.x - img.width / 2,
                pos.y - img.height + this.tileHeight / 2, // Anchor at feet
                img.width, img.height
            );

            // Name tag
            this.ctx.fillStyle = 'white';
            this.ctx.font = '10px monospace';
            this.ctx.textAlign = 'center';
            this.ctx.fillText(ent.meta.username, pos.x, pos.y - h + 5);
        } else {
            // Fallback Circle
            this.ctx.fillStyle = ent.meta.color || 'hotpink';
            this.ctx.beginPath();
            this.ctx.arc(pos.x, pos.y + this.tileHeight / 2 - 10, 10, 0, Math.PI * 2);
            this.ctx.fill();
        }
    }
}
