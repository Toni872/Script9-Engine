/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // Brand accent
        emerald: {
          50:  '#ecfdf5',
          100: '#d1fae5',
          200: '#a7f3d0',
          300: '#6ee7b7',
          400: '#34d399',
          500: '#10b981', // PRIMARY ACCENT
          600: '#059669',
          700: '#047857',
          800: '#065f46',
          900: '#064e3b',
          950: '#022c22',
        },
        // Base surfaces
        slate: {
          50:  '#f8fafc',
          100: '#f1f5f9',
          200: '#e2e8f0',
          300: '#cbd5e1',
          400: '#94a3b8',
          500: '#64748b',
          600: '#475569',
          700: '#334155',
          800: '#1e293b',
          900: '#0f172a',
          950: '#020617', // BASE BACKGROUND
        },
        // Semantic custom tokens
        'script9': {
          bg:       '#020617', // slate-950
          surface:  '#0f172a', // slate-900
          border:   '#1e293b', // slate-800
          accent:   '#10b981', // emerald-500
          'accent-soft': 'rgba(16,185,129,0.15)',
          'accent-glow': 'rgba(16,185,129,0.39)',
          'text-primary':   '#f8fafc', // slate-50
          'text-secondary': '#94a3b8', // slate-400
          'text-tertiary':  '#64748b', // slate-500
          danger: '#ef4444', // red-500
        },
      },

      fontFamily: {
        'space': ['Space Grotesk', 'sans-serif'],
        'inter': ['Inter', 'sans-serif'],
        'mono':  ['JetBrains Mono', 'monospace'],
      },

      boxShadow: {
        'script9-glow':    '0 4px 14px 0 rgba(16,185,129,0.39)',
        'script9-glow-lg': '0 8px 30px 0 rgba(16,185,129,0.45)',
        'script9-glow-xl': '0 16px 60px 0 rgba(16,185,129,0.55)',
        'script9-card':    '0 1px 3px 0 rgba(0,0,0,0.5), 0 1px 2px -1px rgba(0,0,0,0.5)',
      },

      borderRadius: {
        '2xl': '1rem',
        '3xl': '1.5rem',
      },

      backgroundImage: {
        'grid-subtle': `
          linear-gradient(to right,  rgba(255,255,255,0.03) 1px, transparent 1px),
          linear-gradient(to bottom, rgba(255,255,255,0.03) 1px, transparent 1px)
        `,
        'gradient-radial': 'radial-gradient(var(--tw-gradient-stops))',
      },

      backgroundSize: {
        'grid': '4rem 4rem',
      },

      animation: {
        'spin-cube':          'spin-cube 20s linear infinite',
        'float-head':         'float-head 6s ease-in-out infinite',
        'gradient-shift':     'gradient-shift 8s ease infinite',
        'pulse-glow':         'pulse-glow 2s ease-in-out infinite',
        'shimmer-slide':      'shimmer-slide 2s infinite',
        'text-gradient-flow': 'text-gradient-flow 4s ease infinite',
        'ripple':             'ripple-animation 0.6s ease-out',
        'slide-up':           'slideUp 0.5s cubic-bezier(0.16,1,0.3,1)',
        'fade-in':            'fadeIn 0.4s ease',
      },

      keyframes: {
        'spin-cube': {
          '0%':   { transform: 'rotateX(0deg)   rotateY(0deg)' },
          '100%': { transform: 'rotateX(360deg) rotateY(360deg)' },
        },
        'float-head': {
          '0%, 100%': { transform: 'translateY(0px)' },
          '50%':      { transform: 'translateY(-20px)' },
        },
        'gradient-shift': {
          '0%, 100%': { backgroundPosition: '0% 50%' },
          '50%':      { backgroundPosition: '100% 50%' },
        },
        'pulse-glow': {
          '0%, 100%': { boxShadow: '0 0 20px rgba(16,185,129,0.3)' },
          '50%':      { boxShadow: '0 0 40px rgba(16,185,129,0.6), 0 0 80px rgba(16,185,129,0.2)' },
        },
        'shimmer-slide': {
          '0%':   { transform: 'translateX(-100%)' },
          '100%': { transform: 'translateX(100%)' },
        },
        'text-gradient-flow': {
          '0%, 100%': { backgroundPosition: '0% 50%' },
          '50%':      { backgroundPosition: '100% 50%' },
        },
        'ripple-animation': {
          '0%':   { transform: 'scale(0)', opacity: '1' },
          '100%': { transform: 'scale(4)', opacity: '0' },
        },
        'slideUp': {
          '0%':   { transform: 'translateY(20px)', opacity: '0' },
          '100%': { transform: 'translateY(0)',     opacity: '1' },
        },
        'fadeIn': {
          '0%':   { opacity: '0' },
          '100%': { opacity: '1' },
        },
      },
    },
  },
  plugins: [],
}
