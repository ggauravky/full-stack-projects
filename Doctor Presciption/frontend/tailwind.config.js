/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      fontFamily: {
        display: ['"DM Sans"', "sans-serif"],
        body: ['"Inter"', "sans-serif"],
      },
      colors: {
        primary: "#2F80ED",
        accent: "#10B981",
        muted: "#F4F6FB",
      },
    },
  },
  plugins: [],
};
