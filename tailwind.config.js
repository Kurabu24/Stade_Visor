/** @type {import('tailwindcss').Config} */
module.exports = {
    // Enables class-based dark mode (important!)
    content: [
        './templates/*.html',  // Flask or Django template files
        './static/*.js',       // JS files (optional)
    ],
    darkMode: 'class',
    theme: {
        extend: {},
    },
    plugins: [],
    variants: {
        extend: {
            backgroundColor: ['active'],
            // ...
            borderColor: ['focus-visible', 'first'],
            // ...
            textColor: ['visited'],
        }
    },
}
