module.exports = {
    content: [
        // Main templates directory of the project.
        "../../../templates/**/*.html",
    ],
    plugins: [
        require("@tailwindcss/forms"),
        require("@tailwindcss/typography"),
        require("@tailwindcss/line-clamp"),
        require("@tailwindcss/aspect-ratio"),
    ],
    darkMode: "class",
    theme: {
        extend: {
            colors: {
                "pokemon-yellow": "#ffcc00",
                "pokemon-bug": "#94bc4a",
                "pokemon-dark": "#736c75",
                "pokemon-dragon": "#6a7baf",
                "pokemon-electric": "#e5c531",
                "pokemon-fairy": "#e397d1",
                "pokemon-fire": "#ea7a3c",
                "pokemon-grass": "#71c558",
                "pokemon-steel": "#89a1b0",
                "pokemon-water": "#539ae2",
                "pokemon-psychic": "#e5709b",
                "pokemon-ground": "#cc9f4f",
                "pokemon-ice": "#70cbd4",
                "pokemon-flying": "#7da6de",
                "pokemon-ghost": "#846ab6",
                "pokemon-normal": "#aab09f",
                "pokemon-poison": "#b468b7",
                "pokemon-rock": "#b2a061",
                "pokemon-fighting": "#cb5f48",
                "pokemon-shadow": "#7b62a3",
                "pokemon-unknown": "#757575",
            },
        },
        container: {
            center: true,
        },
    },
    safelist: [
        {
            pattern: /^bg-pokemon-+/,
        },
    ],
};
