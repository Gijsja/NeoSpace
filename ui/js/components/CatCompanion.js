/**
 * Cat Companion Component
 * Encapsulates logic for the Emotional Intelligence Cat Widget.
 */

document.addEventListener('alpine:init', () => {
    Alpine.data('catCompanion', (defaultMode = 'cute') => ({
        visible: false,
        cat: 'Loading...',
        // Relationship Data
        relationship_label: '',
        status_tag: '',

        state: 'Idle',
        line: '...',
        avatar: null,
        sound: null,
        mode: defaultMode,
        timeout: null,
        audioPlayer: null,

        init() {
            // Preload a silence file or init audio context if needed?
            // For now, just logging.
            console.log('[CatCompanion] Initialized 🐱');
        },

        getCsrfToken() {
            return document.querySelector('meta[name="csrf-token"]')?.getAttribute('content');
        },

        async speak(event) {
            console.log('[CatCompanion] Trigger:', event);

            const csrfToken = this.getCsrfToken();
            if (!csrfToken) {
                console.error('[CatCompanion] CSRF Token missing!');
                return;
            }

            try {
                const res = await fetch('/cats/speak', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': csrfToken
                    },
                    body: JSON.stringify({ event, mode: this.mode })
                });

                if (!res.ok) {
                    throw new Error(`API Error: ${res.status}`);
                }

                const data = await res.json();

                if (data.cat) {
                    this.updateState(data);
                }

            } catch (err) {
                console.warn('[CatCompanion] Speak failed:', err);
            }
        },

        updateState(data) {
            this.cat = data.cat;
            this.state = data.state;
            this.line = data.line;
            this.avatar = data.avatar;
            this.sound = data.sound;

            // New Relationship Data
            this.relationship_label = data.relationship_label || '';
            this.status_tag = data.status_tag || '';

            // Play Audio
            this.playAudio();

            // Dispatch Toast (Penguin UI)
            // Format Title: "Miso [Rival]" or just "Miso" if no label
            const toastTitle = this.relationship_label
                ? `${this.cat} [${this.relationship_label}]`
                : this.cat;

            window.dispatchEvent(new CustomEvent('toast', {
                detail: {
                    title: toastTitle,
                    message: this.line,
                    type: 'info',
                    avatar: this.avatar
                }
            }));

            // Legacy internal state update (optional, mostly unused now)
            this.visible = false;
        },

        playAudio() {
            if (!this.sound) return;

            // Stop previous if playing
            if (this.audioPlayer) {
                this.audioPlayer.pause();
                this.audioPlayer.currentTime = 0;
            }

            const soundUrl = `/static/catsounds/${this.sound}`;
            this.audioPlayer = new Audio(soundUrl);
            this.audioPlayer.volume = 0.4; // Valid volume

            this.audioPlayer.play().catch(e => {
                console.log('[CatCompanion] Audio autoplay blocked or failed:', e);
            });
        },

        dismiss() {
            this.visible = false;
            // Optional: Stop audio on dismiss? 
            // this.audioPlayer?.pause(); 
            clearTimeout(this.timeout);
        }
    }));
});
