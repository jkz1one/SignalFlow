// tailwind.config.js
module.exports = {
  content: [
    "./app/**/*.{js,ts,jsx,tsx}",
    "./app/**/**/*.{js,ts,jsx,tsx}", // optional, redundant if first line has **
    "./components/**/*.{js,ts,jsx,tsx}",
    "./pages/**/*.{js,ts,jsx,tsx}"
  ],
  safelist: [
    'grid-cols-1',
    'grid-cols-2',
    'grid-cols-3',
    'col-span-1',
    'col-span-2',
    'col-span-3',
    // Add any other classes you use dynamically
  ],
  theme: {
    extend: {},
  },
  plugins: [],
}
