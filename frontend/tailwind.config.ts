import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      fontFamily: {
        mono: ["JetBrains Mono", "Fira Code", "Geist Mono", "monospace"],
        sans: ["Inter", "system-ui", "sans-serif"],
      },
      colors: {
        // Neo-brutalist monochrome tokens
        "nb-black": "#000000",
        "nb-white": "#FFFFFF",
        "nb-gray-100": "#F5F5F5",
        "nb-gray-200": "#E5E5E5",
        "nb-gray-400": "#A3A3A3",
        "nb-gray-600": "#525252",
        // Hermes terminal tokens
        "herm-bg": "#090A0F",
        "herm-bg2": "#0D0E11",
        "herm-text": "#E6EDF3",
        "herm-muted": "#6E7681",
        "herm-green": "#3FB950",
        "herm-amber": "#D29922",
      },
      boxShadow: {
        "hard": "4px 4px 0px 0px #000000",
        "hard-sm": "2px 2px 0px 0px #000000",
        "hard-lg": "6px 6px 0px 0px #000000",
        "hard-white": "4px 4px 0px 0px #FFFFFF",
        "hard-inset": "inset 2px 2px 0px 0px #000000",
      },
      keyframes: {
        "pulse-border": {
          "0%, 100%": { borderColor: "#000000", boxShadow: "4px 4px 0px 0px #000000" },
          "50%": { borderColor: "#555555", boxShadow: "4px 4px 0px 0px #555555" },
        },
        "blink": {
          "0%, 100%": { opacity: "1" },
          "50%": { opacity: "0" },
        },
        "scan-line": {
          "0%": { transform: "translateY(-100%)" },
          "100%": { transform: "translateY(100vh)" },
        },
        "slide-in-right": {
          "0%": { transform: "translateX(100%)", opacity: "0" },
          "100%": { transform: "translateX(0)", opacity: "1" },
        },
      },
      animation: {
        "pulse-border": "pulse-border 1.5s ease-in-out infinite",
        "blink": "blink 1s step-end infinite",
        "scan-line": "scan-line 4s linear infinite",
        "slide-in-right": "slide-in-right 0.3s ease-out forwards",
      },
    },
  },
  plugins: [],
};

export default config;
