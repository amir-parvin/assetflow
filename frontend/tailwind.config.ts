import type { Config } from "tailwindcss";

const config: Config = {
  darkMode: "class",
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: ["var(--font-inter)", "system-ui", "sans-serif"],
        mono: ["var(--font-mono)", "JetBrains Mono", "monospace"],
      },
      colors: {
        accent: {
          DEFAULT: "#E5C07B",
          hover: "#D4A843",
          muted: "rgba(229, 192, 123, 0.1)",
        },
      },
      borderRadius: {
        none: "0",
      },
    },
  },
  plugins: [],
};
export default config;
