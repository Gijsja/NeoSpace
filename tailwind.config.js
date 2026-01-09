/** @type {import('tailwindcss').Config} */
export default {
  content: ["./ui/**/*.{html,js}", "./templates/**/*.html"],
  darkMode: 'class',
  theme: {
    extend: {
      fontFamily: {
        sans: ['Inter', 'sans-serif'],
        mono: ['Fira Code', 'monospace'],
      },
      colors: {
        // Base Layout
        'bbs-bg': '#FFFAF0',
        'bbs-surface': '#FFFFFF',
        'bbs-border': '#000000',

        // Neo-Brutalist Palette
        'neo-black': '#000000',
        'neo-white': '#FFFFFF',
        'neo-bg': '#0a0f1a',

        // Accents
        'acid-green': '#a3e635',
        'hot-pink': '#ff6b6b',
        'electric-blue': '#22d3ee',
        'construction-orange': '#fb923c',
        'warm-beige': '#f5f5dc',

        // Aliases
        'neo-green': '#a3e635',
        'neo-pink': '#ff6b6b',
        'neo-blue': '#22d3ee',
        'neo-yellow': '#F3F722',
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
    },
  },
  plugins: [],
}
