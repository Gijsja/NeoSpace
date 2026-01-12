/**
 * Sprint 26: Presence System
 * Handles real-time online status indicators.
 */
document.addEventListener('DOMContentLoaded', () => {
    const socket = io();

    const OnlineManager = {
        onlineUsers: new Set(),

        init() {
            socket.on('connect', () => {
                socket.emit('get_online_users');
            });

            socket.on('user_online', (data) => {
                this.setUserOnline(data.user_id, true);
            });

            socket.on('user_offline', (data) => {
                this.setUserOnline(data.user_id, false);
            });

            socket.on('get_online_users', (data) => {
                // Assuming the backend sends { online_ids: [...] } but checking sockets.py I implemented a return value
                // Socket.IO Ack pattern? Or emit back?
                // Checking sockets.py: it acts as an acknowledgement return if using call, 
                // BUT standard `emit` inside handler is better.
                // My sockets.py implementation: return {"online_ids": ...}
                // This means `socket.emit('get_online_users', (response) => ...)`
            });

            // Correct way to get initial state if backend returns data in ack
            socket.emit('get_online_users', (response) => {
                if (response && response.online_ids) {
                    response.online_ids.forEach(id => this.setUserOnline(id, true));
                }
            });
        },

        setUserOnline(userId, isOnline) {
            if (isOnline) {
                this.onlineUsers.add(userId);
            } else {
                this.onlineUsers.delete(userId);
            }
            this.updateUI(userId, isOnline);
        },

        updateUI(userId, isOnline) {
            const avatars = document.querySelectorAll(`.user-avatar[data-user-id="${userId}"]`);
            avatars.forEach(el => {
                // Check if indicator exists
                let indicator = el.querySelector('.online-indicator');
                if (isOnline) {
                    if (!indicator) {
                        indicator = document.createElement('div');
                        indicator.className = "online-indicator absolute -bottom-1 -right-1 w-3 h-3 bg-neon-green border-2 border-black rounded-full z-10 shadow-sm";
                        el.appendChild(indicator);
                    }
                } else {
                    if (indicator) indicator.remove();
                }
            });

            // Also update "x Users Online" in marquee if possible
            // Not strictly required but nice to have.
        }
    };

    OnlineManager.init();
    window.OnlineManager = OnlineManager;
});
