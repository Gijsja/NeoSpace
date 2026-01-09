/**
 * WallMain.js
 * Entry point for the Wall UI.
 * Orchestrates modules and initialization.
 */

import * as Network from './WallNetwork.js';
import * as Renderer from './WallRenderer.js';
import * as State from './WallState.js';
import * as ModuleForm from './WallModules.js';
import * as EditForm from './WallEdit.js';
import WallStickers from './WallStickers.js';

// Init
// Init
(async () => {
    console.log("[WallMain] Starting initialization...");
    try {
        // 1. Initial Data Fetch
        console.log("[WallMain] Fetching profile data...");
        const data = await Network.fetchProfileData();
        console.log("[WallMain] Data fetched:", data);
        if (!data) {
            console.error("[WallMain] No data returned.");
            return;
        }

        // 2. Initial Render
        console.log("[WallMain] Rendering profile...");
        Renderer.renderProfile(data);

        // 3. Setup Edit Forms
        EditForm.setupEditForm({
            onSuccess: async () => {
                const newData = await Network.fetchProfileData();
                if (newData) Renderer.renderProfile(newData);
            },
            onRender: (updatedData) => {
                // For partial updates like avatar
                Renderer.renderProfile(updatedData);
            }
        });

        // 4. Setup Module Forms
        ModuleForm.setupModuleForm({
            onSuccess: async () => {
                const newData = await Network.fetchProfileData();
                if (newData) Renderer.renderProfile(newData);
            }
        });

        // 5. Setup Stickers
        // Initialize the WallStickers manager
        const stickerManager = new WallStickers('sticker-canvas');
        State.setStickerManager(stickerManager); // Store in state if needed

        // Set context and load stickers
        if (data) {
            stickerManager.setProfile(data.user_id, data.is_own);
            stickerManager.load(data.stickers);
        }

        // Expose for debugging
        window.wallState = State.state;
        window.fetchProfile = async () => {
            const d = await Network.fetchProfileData();
            if (d) {
                Renderer.renderProfile(d);
                // Refresh stickers too
                stickerManager.setProfile(d.user_id, d.is_own);
                stickerManager.load(d.stickers);
            }
        };

        console.log("[WallMain] Initialization complete.");
        window.WallMainLoaded = true;

    } catch (e) {
        console.error("[WallMain] Critical Error:", e);
        // Show error on screen if possible
        const loadingEl = document.getElementById('loading');
        if (loadingEl) loadingEl.innerHTML = `<div class="bg-red-500 text-white p-4 font-bold">CRITICAL UI ERROR: ${e.message}</div>`;
    }
})();
