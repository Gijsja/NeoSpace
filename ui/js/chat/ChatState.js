/**
 * ChatState.js
 * Central shared state for the Chat application.
 */

export const state = {
    currentUser: localStorage.getItem('neospace_username') || '',
    currentRoom: new URLSearchParams(window.location.search).get('room') || 'general',
    messageIds: new Set(),
    isLoading: false,
    typingUsersList: new Set(),
    socket: null, // Socket.io instance
    isTyping: false,
    typingTimeout: null,
    searchTimeout: null,
    pendingDeleteId: null
};

export function cleanupChat() {
    if (state.socket) {
        state.socket.disconnect();
        state.socket = null;
    }
    state.messageIds.clear();
    state.typingUsersList.clear();
}
