/**
 * WallState.js
 * Shared state for the Wall modules.
 */

export const state = {
    userId: new URLSearchParams(window.location.search).get('user_id'),
    currentUserData: null,
    stickerManager: null,
    voiceRecorder: null,
    activeModuleMenu: null
};

export const themes = {
    'default': 'linear-gradient(135deg, #0f172a 0%, #1e293b 100%)',
    'dark': 'linear-gradient(to bottom, #000000, #111111)',
    'retro': 'linear-gradient(45deg, #2b0a3d, #c53c8d)',
    'zen': 'linear-gradient(to bottom, #1a2f23, #2f4f4f)'
};

export function setCurrentUserData(data) {
    state.currentUserData = data;
}

export function setStickerManager(mgr) {
    state.stickerManager = mgr;
}

export function setVoiceRecorder(vr) {
    state.voiceRecorder = vr;
}
