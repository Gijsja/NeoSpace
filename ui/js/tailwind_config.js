/**
 * NeoSpace Tailwind Configuration (Runtime)
 * Standardizes the Neubrutalist Design System across the app.
 * Loaded by base.html for the standalone Tailwind script.
 */
window.tailwind.config = {
    darkMode: 'class', // Manual toggling
    theme: {
        extend: {
            fontFamily: {
                sans: ['"Courier New"', 'Courier', 'monospace'], // Default to mono for brutalism
                mono: ['"Courier New"', 'Courier', 'monospace'],
            },
            colors: {
                // Base
                'black': '#000000',
                'white': '#ffffff',
                'gray-light': '#f5f5f5',
                'gray-dark': '#333333',

                // Neobrutalist Palette
                'neon-green': '#ccff00',
                'hot-pink': '#ff0055',
                'cyber-blue': '#00ccff',
                'electric-yellow': '#ffff00',
                'acid-green': '#39ff14',
                'purple': '#9d00ff',
                'orange': '#ff8800',

                // Semantic Aliases for compatibility
                'neo-bg': '#f5f5f5',
                'bbs-bg': '#f5f5f5', // Deprecated but aliased to gray-light
            },
            boxShadow: {
                'hard': '4px 4px 0px 0px #000000',
                'hard-sm': '2px 2px 0px 0px #000000',
                'hard-md': '6px 6px 0px 0px #000000',
                'hard-xl': '8px 8px 0px 0px #000000',
            },
            animation: {
                'marquee': 'marquee 20s linear infinite',
                'fade-in': 'fadeIn 0.4s ease-out',
                'pop': 'pop 0.2s ease-out',
                'glitch': 'glitch 0.3s cubic-bezier(0.25, 0.46, 0.45, 0.94) both infinite',
            },
            keyframes: {
                marquee: {
                    '0%': { transform: 'translateX(0%)' },
                    '100%': { transform: 'translateX(-100%)' }
                },
                fadeIn: {
                    '0%': { opacity: '0', transform: 'translateY(15px)' },
                    '100%': { opacity: '1', transform: 'translateY(0)' },
                },
                pop: {
                    '0%': { transform: 'scale(0.95)' },
                    '50%': { transform: 'scale(1.02)' },
                    '100%': { transform: 'scale(1)' },
                },
                glitch: {
                    '0%': { transform: 'translate(0)' },
                    '20%': { transform: 'translate(-2px, 2px)' },
                    '40%': { transform: 'translate(-2px, -2px)' },
                    '60%': { transform: 'translate(2px, 2px)' },
                    '80%': { transform: 'translate(2px, -2px)' },
                    '100%': { transform: 'translate(0)' },
                },
            }
        }
    }
};
