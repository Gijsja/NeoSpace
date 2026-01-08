/**
 * ChatSocket.js
 * Wraps socket.io functionality and event handling.
 */

import { state } from './ChatState.js';

export function initSocket(callbacks) {
    console.log('ChatSocket initializing...');
    
    try {
        if (!state.socket) {
            state.socket = io();
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

        s.on('reconnect', () => {
            if (callbacks.onReconnect) callbacks.onReconnect();
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
