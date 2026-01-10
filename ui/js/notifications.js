/**
 * Sprint 22: Live Wire UI
 * Handles notification polling, badge updates, and toast alerts.
 */

const NotificationManager = {
    state: {
        unreadCount: 0,
        pollingInterval: 15000, // 15 seconds
        timer: null
    },

    init() {
        this.bellBadge = document.getElementById('notification-badge');
        this.bellBtn = document.getElementById('notification-bell-btn');
        this.toastContainer = document.getElementById('toast-container');

        // Initial check
        this.checkUnread();

        // Start polling
        this.startPolling();

        // Bell Click
        if (this.bellBtn) {
            this.bellBtn.onclick = () => {
                window.location.href = '/notifications/center';
            };
        }
    },

    startPolling() {
        this.timer = setInterval(() => this.checkUnread(), this.state.pollingInterval);
    },

    async checkUnread() {
        try {
            const res = await fetch('/notifications/unread-count');
            const data = await res.json();

            if (data.ok) {
                this.updateBadge(data.count);

                // If count increased significantly, maybe show toast?
                // For now, just badge.
                if (data.count > this.state.unreadCount && data.count > 0) {
                    // Start animation on bell
                    if (this.bellBtn) {
                        this.bellBtn.classList.add('animate-bounce');
                        setTimeout(() => this.bellBtn.classList.remove('animate-bounce'), 1000);
                    }
                }
                this.state.unreadCount = data.count;
            }
        } catch (e) {
            console.error("Notification Poll Failed", e);
        }
    },

    updateBadge(count) {
        if (!this.bellBadge) return;

        if (count > 0) {
            this.bellBadge.classList.remove('hidden');
            this.bellBadge.innerText = count > 99 ? '99+' : count;
        } else {
            this.bellBadge.classList.add('hidden');
        }
    },

    // To be called by other components (e.g. WebSocket or AJAX actions)
    showToast(message, type = 'info') {
        window.dispatchEvent(new CustomEvent('toast', {
            detail: {
                title: 'Notification',
                message: message,
                type: type
            }
        }));
    },

    async markAllRead() {
        try {
            const res = await fetch('/notifications/mark-all-read', {
                method: 'POST'
            });
            const data = await res.json();
            if (data.ok) {
                this.updateBadge(0);
                this.state.unreadCount = 0;
                // Reload page if on center
                if (window.location.pathname.includes('/notifications/center')) {
                    window.location.reload();
                }
            }
        } catch (e) {
            console.error(e);
        }
    }
};

document.addEventListener('DOMContentLoaded', () => {
    NotificationManager.init();
});

// Global export
window.NotificationManager = NotificationManager;
