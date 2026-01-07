/** @type {import('tailwindcss').Config} */
export default {
  content: ["./ui/**/*.{html,js}"],
  theme: {
    extend: {
      colors: {
        'neo-bg': '#0a0f1a',
        'neo-surface': 'rgba(30, 41, 59, 0.85)',
        'neo-border': 'rgba(71, 85, 105, 0.5)',
        'neo-accent': '#60a5fa',
        'neo-accent-glow': 'rgba(96, 165, 250, 0.4)',
        // Legacy aliases for compatibility
        'bbs-bg': '#0a0f1a',
        'bbs-surface': 'rgba(30, 41, 59, 0.85)',
        'bbs-border': 'rgba(71, 85, 105, 0.5)',
        'bbs-accent': '#60a5fa',
        'bbs-accent-glow': 'rgba(96, 165, 250, 0.4)',
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
      },
      animation: {
        'fade-in': 'fadeIn 0.4s ease-out',
        'pop': 'pop 0.2s ease-out',
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0', transform: 'translateY(15px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        pop: {
          '0%': { transform: 'scale(0.95)' },
          '50%': { transform: 'scale(1.02)' },
          '100%': { transform: 'scale(1)' },
        },
      },
      boxShadow: {
        'glow': '0 0 20px rgba(96, 165, 250, 0.5)',
        'glow-lg': '0 0 40px rgba(96, 165, 250, 0.6)',
      },
    },
  },
  plugins: [],
}
