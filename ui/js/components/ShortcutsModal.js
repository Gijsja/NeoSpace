/**
 * ShortcutsModal.js
 * Displays a modal with keyboard shortcuts when '?' is pressed.
 */

class ShortcutsModal {
    constructor() {
        this.isVisible = false;
        this.init();
    }

    init() {
        // Listen for global keydown
        document.addEventListener('keydown', (e) => {
            // Ignore if typing in input, textarea, or contenteditable
            if (['INPUT', 'TEXTAREA'].includes(e.target.tagName) || e.target.isContentEditable) {
                return;
            }

            if (e.key === '?' && e.shiftKey) {
                this.toggle();
            }

            if (e.key === 'Escape' && this.isVisible) {
                this.close();
            }
        });
    }

    createOverlay() {
        const overlay = document.createElement('div');
        overlay.id = 'shortcuts-modal';
        overlay.className = 'fixed inset-0 bg-black/80 z-[9999] flex items-center justify-center backdrop-blur-sm animate-fade-in';
        overlay.onclick = (e) => {
            if (e.target === overlay) this.close();
        };

        const content = `
            <div class="bg-gray-900 border-2 border-emerald-500 p-6 max-w-md w-full shadow-[4px_4px_0px_0px_rgba(16,185,129,1)]">
                <div class="flex justify-between items-center mb-6">
                    <h2 class="text-2xl font-bold text-emerald-500 font-mono">
                        <span class="mr-2">⌨️</span>KEYBOARD SHORTCUTS
                    </h2>
                    <button onclick="document.getElementById('shortcuts-modal').remove()" class="text-gray-400 hover:text-white">✕</button>
                </div>
                
                <div class="space-y-4 font-mono text-sm">
                    <div class="flex justify-between items-center">
                        <span class="text-gray-300">Show this help</span>
                        <kbd class="bg-gray-800 px-2 py-1 rounded border border-gray-700 text-emerald-400">Shift + ?</kbd>
                    </div>
                    <div class="flex justify-between items-center">
                        <span class="text-gray-300">Send Message</span>
                        <kbd class="bg-gray-800 px-2 py-1 rounded border border-gray-700 text-emerald-400">Enter</kbd>
                    </div>
                    <div class="flex justify-between items-center">
                        <span class="text-gray-300">Connection Doctor</span>
                        <kbd class="bg-gray-800 px-2 py-1 rounded border border-gray-700 text-emerald-400">Ctrl + Shift + D</kbd>
                    </div>
                     <div class="flex justify-between items-center">
                        <span class="text-gray-300">Close Modal</span>
                        <kbd class="bg-gray-800 px-2 py-1 rounded border border-gray-700 text-emerald-400">Esc</kbd>
                    </div>
                </div>
                
                <div class="mt-6 pt-4 border-t border-gray-800 text-center text-xs text-gray-500">
                    BOLT // NEOSPACE V${window.NEOSPACE_VERSION || '0.5.7'}
                </div>
            </div>
        `;

        overlay.innerHTML = content;
        return overlay;
    }

    toggle() {
        if (this.isVisible) {
            this.close();
        } else {
            this.open();
        }
    }

    open() {
        if (document.getElementById('shortcuts-modal')) return;

        const modal = this.createOverlay();
        document.body.appendChild(modal);
        this.isVisible = true;
    }

    close() {
        const modal = document.getElementById('shortcuts-modal');
        if (modal) {
            modal.remove();
        }
        this.isVisible = false;
    }
}

// Auto-init
window.shortcutsModal = new ShortcutsModal();
