/** @type {import('tailwindcss').Config} */
module.exports = {
    darkMode: "class",
    content: [
        "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
        "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
        "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
    ],
    theme: {
        extend: {
            fontFamily: {
                sans: ["var(--font-inter)"],
                serif: ["var(--font-playfair)"],
            },
            colors: {
                emerald: {
                    400: "#34d399",
                    500: "#10b981",
                    900: "#064e3b",
                },
                cyan: {
                    400: "#22d3ee",
                    500: "#06b6d4",
                },
                lime: {
                    400: "#bef264",
                    500: "#84cc16",
                    accent: "#CFFF04", // The bright neon lime from the reference
                },
            },
            animation: {
                "glow-pulse": "glow-pulse 4s cubic-bezier(0.4, 0, 0.6, 1) infinite",
                "fade-in-up": "fade-in-up 0.5s ease-out forwards",
            },
            keyframes: {
                "glow-pulse": {
                    "0%, 100%": { opacity: "0.4", transform: "scale(1)" },
                    "50%": { opacity: "0.8", transform: "scale(1.1)" },
                },
                "fade-in-up": {
                    "0%": { opacity: "0", transform: "translateY(20px)" },
                    "100%": { opacity: "1", transform: "translateY(0)" },
                },
            },
        },
    },
    plugins: [],
};
