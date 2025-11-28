/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          DEFAULT: '#222222',
          light: '#333333',
        },
        yellow: {
          shizzo: '#eebe22',
          light: '#f5d042',
        },
      },
    },
  },
  plugins: [],
}