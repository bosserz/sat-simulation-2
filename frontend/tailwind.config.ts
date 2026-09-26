import type { Config } from "tailwindcss";

export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        intsight: "#002a5c",
        ink: "#172033",
        paper: "#f6f7fb",
        aqua: "#0f766e",
        amber: "#b45309"
      },
      fontFamily: {
        sans: ["Anuphan", "ui-sans-serif", "system-ui", "sans-serif"]
      },
      boxShadow: {
        soft: "0 16px 40px rgba(23, 32, 51, 0.08)"
      }
    }
  },
  plugins: []
} satisfies Config;
