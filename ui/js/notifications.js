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
        if (!this.toastContainer) return;

        const toast = document.createElement('div');
        const bgClass = type === 'error' ? 'bg-red-500 text-white' : 
                        type === 'success' ? 'bg-acid-green text-black' : 
                        'bg-black text-white';
                        
        toast.className = `${bgClass} p-4 border-2 border-transparent shadow-hard-xl pointer-events-auto transform transition-all duration-300 translate-x-32 opacity-0 flex items-center gap-3 min-w-[200px]`;
        toast.innerHTML = `
            <i class="ph-bold ${type === 'error' ? 'ph-warning' : type === 'success' ? 'ph-check' : 'ph-info'}"></i>
            <span class="font-bold text-sm font-mono uppercase">${message}</span>
        `;
        
        this.toastContainer.appendChild(toast);
        
        // Animate In
        requestAnimationFrame(() => {
            toast.classList.remove('translate-x-32', 'opacity-0');
        });
        
        // Remove after 3s
        setTimeout(() => {
            toast.classList.add('translate-x-32', 'opacity-0');
            setTimeout(() => toast.remove(), 300);
        }, 3000);
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
        } catch(e) {
            console.error(e);
        }
    }
};

document.addEventListener('DOMContentLoaded', () => {
    NotificationManager.init();
});

// Global export
window.NotificationManager = NotificationManager;
