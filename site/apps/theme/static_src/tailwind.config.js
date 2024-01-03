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
};
