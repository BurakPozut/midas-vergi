/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        navy: {
          800: "#1a1f2c",
          900: "#0f1219",
        },
      },
      keyframes: {
        "fade-in": {
          "0%": {
            opacity: "0",
            transform: "translateY(20px)",
          },
          "100%": {
            opacity: "1",
            transform: "translateY(0)",
          },
        },
      },
      animation: {
        "fade-in": "fade-in 0.8s ease-out forwards",
      },
      animationDelay: {
        200: "200ms",
        400: "400ms",
        600: "600ms",
        800: "800ms",
      },
      fontFamily: {
        sans: ["var(--font-geist-sans)"],
        mono: ["var(--font-geist-mono)"],
      },
    },
  },
  plugins: [
    function ({ addUtilities, theme }) {
      const animationDelays = theme("animationDelay");
      const utilities = Object.entries(animationDelays).map(([key, value]) => ({
        [`.animation-delay-${key}`]: {
          "animation-delay": value,
        },
      }));
      addUtilities(utilities);
    },
  ],
};
