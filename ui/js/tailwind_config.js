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
                sans: ['Inter', 'sans-serif'],
                mono: ['Fira Code', 'monospace'],
            },
            fontSize: {
                'xs': ['0.75rem', { lineHeight: '1rem' }],
                'sm': ['0.875rem', { lineHeight: '1.25rem' }],
                'base': ['1rem', { lineHeight: '1.5rem' }],
                'lg': ['1.125rem', { lineHeight: '1.75rem' }],
                'xl': ['1.25rem', { lineHeight: '1.75rem' }],
                '2xl': ['1.5rem', { lineHeight: '2rem' }],
                '3xl': ['1.875rem', { lineHeight: '2.25rem' }],
                '4xl': ['2.25rem', { lineHeight: '2.5rem' }],
                '5xl': ['3rem', { lineHeight: '1' }],
                '6xl': ['3.75rem', { lineHeight: '1' }],
            },
            fontWeight: {
                normal: '400',
                bold: '700',
                black: '900', // Heavy usage in headers
            },
            colors: {
                // Base Layout
                'bbs-bg': '#FFFAF0',      // Floral White (Light Mode Base)
                'bbs-surface': '#FFFFFF',
                'bbs-border': '#000000',

                // Neo-Brutalist Palette (Penguin UI)
                'neo-black': '#000000',
                'neo-white': '#FFFFFF',
                'neo-bg': '#0a0f1a',      // Dark Mode Base

                // Accents (The "Acid" Pop)
                'acid-green': '#a3e635',  // Primary Highlight
                'hot-pink': '#ff6b6b',    // Destructive / Attention
                'electric-blue': '#22d3ee',
                'construction-orange': '#fb923c',
                'warm-beige': '#f5f5dc',

                // Semantic Aliases
                'neo-green': '#a3e635',
                'neo-pink': '#ff6b6b',
                'neo-blue': '#22d3ee',
                'neo-yellow': '#F3F722', // Warning
            },
            boxShadow: {
                'hard': '4px 4px 0px 0px #000000',
                'hard-sm': '2px 2px 0px 0px #000000',
                'hard-md': '6px 6px 0px 0px #000000',
                'hard-xl': '8px 8px 0px 0px #000000',
                'glow': '0 0 20px rgba(96, 165, 250, 0.5)',
            },
            animation: {
                'marquee': 'marquee 20s linear infinite',
                'fade-in': 'fadeIn 0.4s ease-out',
                'pop': 'pop 0.2s ease-out',
                'glitch': 'glitch 0.3s cubic-bezier(0.25, 0.46, 0.45, 0.94) both infinite',
            },
            keyframes: {
                marquee: {
                    '0%': { transform: 'translateX(100%)' },
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
