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

// Init
(async () => {
    // 1. Initial Data Fetch
    const data = await Network.fetchProfileData();
    if (!data) return;

    // 2. Initial Render
    Renderer.renderProfile(data);

    // 3. Setup Edit Forms
    EditForm.setupEditForm({
        onSuccess: async () => {
             const newData = await Network.fetchProfileData();
             if(newData) Renderer.renderProfile(newData);
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
             if(newData) Renderer.renderProfile(newData);
        }
    });

    // 5. Setup Stickers
    // Note: StickerManager is global for now, but plugged into Renderer
    if (!state.stickerManager) {
        if (typeof StickerManager !== 'undefined') {
            const mgr = new StickerManager(
                'sticker-canvas', 
                data.is_own, 
                data.viewer_id, 
                data.user_id
            );
            State.setStickerManager(mgr);
            mgr.setStickers(data.stickers);
            
            if (data.viewer_id) {
                Renderer.setupPalette();
            }
        }
    }

    // Expose for debugging
    window.wallState = State.state;
    // Keep window.fetchProfile for legacy external calls if any
    window.fetchProfile = async () => {
        const d = await Network.fetchProfileData();
        if(d) Renderer.renderProfile(d);
    };

})();

// Convenience re-export helper if needed, but this is an entry point.
