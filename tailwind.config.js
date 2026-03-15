import daisyui from 'daisyui'

/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{vue,js,ts,jsx,tsx}'],
  theme: {
    extend: {
      fontFamily: {
        sans: ['YekanBakh', 'Tahoma', 'Segoe UI', 'Arial', 'sans-serif']
      }
    }
  },
  daisyui: {
    themes: ['silk', 'light']
  },
  plugins: [daisyui]
}
