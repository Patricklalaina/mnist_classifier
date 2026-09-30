/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx}'],
  theme: {
    extend: {
      colors: {
        // Neutral dark surfaces with a single red accent. Validated against the
        // card surface (#1a1a19): accent 5.16:1, ink 17.4:1, secondary 9.7:1.
        page: '#111110',
        card: '#1a1a19',
        edge: '#2e2e2b',
        track: '#232320',
        ink: { DEFAULT: '#ffffff', muted: '#c3c2b7', faint: '#8f8d84' },
        accent: { DEFAULT: '#f2555a', hover: '#d8444a' },
      },
      borderRadius: { card: '20px' },
    },
  },
  plugins: [],
}
