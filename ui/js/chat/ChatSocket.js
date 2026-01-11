/**
 * ChatSocket.js
 * Wraps socket.io functionality and event handling.
 */

import { state } from './ChatState.js';

export function initSocket(callbacks) {
    console.log('ChatSocket initializing...');

    try {
        if (!state.socket) {
            // Bolt ⚡: Exponential backoff for reconnection
            // randomizationFactor: 0.5 (default) -> jitter between 50% below and 50% above the delay
            state.socket = io({
                reconnection: true,
                reconnectionDelay: 1000,      // Start with 1s
                reconnectionDelayMax: 10000,  // Cap at 10s (don't hammer server)
                reconnectionAttempts: Infinity,
                randomizationFactor: 0.5,
                timeout: 20000
            });
        }

        const s = state.socket;

        s.on('connect', () => {
            if (callbacks.onConnect) callbacks.onConnect();
        });

        s.on('connected', (data) => {
            // Join room
            s.emit('join_room', { room: state.currentRoom });
            if (data && data.username) {
                state.currentUser = data.username;
                localStorage.setItem('neospace_username', state.currentUser);
            }
        });

        s.on('room_joined', () => {
            s.emit('request_backfill', { after_id: 0 });
        });

        s.on('disconnect', () => {
            if (callbacks.onDisconnect) callbacks.onDisconnect();
        });

        s.on('reconnect', (attemptNumber) => {
            console.log(`[ChatSocket] Reconnected after ${attemptNumber} attempts`);
            if (callbacks.onReconnect) callbacks.onReconnect();
        });

        s.on('reconnect_attempt', (attemptNumber) => {
            console.log(`[ChatSocket] Reconnect attempt #${attemptNumber}...`);
        });

        s.on('reconnect_error', (error) => {
            console.log('[ChatSocket] Reconnect error:', error);
        });

        s.on('connect_error', (error) => {
            console.log('[ChatSocket] Connection error:', error);
        });

        s.on('message', (msg) => {
            if (callbacks.onMessage) callbacks.onMessage(msg);
        });

        s.on('backfill', (payload) => {
            if (callbacks.onBackfill) callbacks.onBackfill(payload);
        });

        s.on('typing', (data) => {
            if (callbacks.onTyping) callbacks.onTyping(data);
        });

        s.on('stop_typing', (data) => {
            if (callbacks.onStopTyping) callbacks.onStopTyping(data);
        });

    } catch (e) {
        console.error("Socket Init Error:", e);
    }
}

export function sendMessage(content) {
    if (!state.socket) return;
    const user = state.currentUser || 'anonymous';
    state.socket.emit('send_message', { user, content });
}

export function sendTyping(isTyping) {
    if (!state.socket) return;
    const user = state.currentUser || 'anonymous';
    const event = isTyping ? 'typing' : 'stop_typing';
    state.socket.emit(event, { user });
}
