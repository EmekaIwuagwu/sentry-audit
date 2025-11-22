/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // Deep Red Theme
        primary: {
          DEFAULT: '#8B0000',
          50: '#FFE5E5',
          100: '#FFCCCC',
          200: '#FF9999',
          300: '#FF6666',
          400: '#FF3333',
          500: '#DC143C',
          600: '#B22222',
          700: '#8B0000',
          800: '#660000',
          900: '#4D0000',
        },
        background: {
          dark: '#0F0F0F',
          card: '#1A1A1A',
          elevated: '#252525',
        },
        text: {
          primary: '#FFFFFF',
          secondary: '#B0B0B0',
          muted: '#6B6B6B',
        },
        border: {
          subtle: '#2A2A2A',
        },
        severity: {
          critical: '#8B0000',
          high: '#DC143C',
          medium: '#F59E0B',
          low: '#3B82F6',
          info: '#6B7280',
        },
      },
      fontFamily: {
        sans: ['-apple-system', 'BlinkMacSystemFont', 'Segoe UI', 'Roboto', 'sans-serif'],
        mono: ['Courier New', 'monospace'],
      },
      boxShadow: {
        'glow': '0 0 20px rgba(139, 0, 0, 0.3)',
        'glow-strong': '0 0 30px rgba(139, 0, 0, 0.5)',
      },
      animation: {
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'fade-in': 'fadeIn 0.5s ease-in-out',
        'slide-up': 'slideUp 0.5s ease-out',
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        slideUp: {
          '0%': { transform: 'translateY(20px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
      },
    },
  },
  plugins: [],
}
