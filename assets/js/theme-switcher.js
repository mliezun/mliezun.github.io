// Update button icon and tooltip
function updateThemeToggle(theme) {
    const themeToggle = document.getElementById('theme-toggle');
    const img = themeToggle.querySelector('img');
    let icon = '/assets/images/circle-half.svg';
    let label = 'Auto';
    if (theme === 'light') {
        icon = '/assets/images/circle-empty.svg';
        label = 'Light';
    } else if (theme === 'dark') {
        icon = '/assets/images/circle-filled.svg';
        label = 'Dark';
    }
    img.src = icon;
    img.alt = label + ' mode';
    themeToggle.title = 'Theme: ' + label;
}

function getEffectiveTheme(theme) {
    if (theme === 'auto') {
        return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
    }
    return theme;
}

const HLJS_THEMES = {
    light: 'https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.11.1/styles/github.min.css',
    dark: 'https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.11.1/styles/atom-one-dark.min.css',
};

function updateHljsTheme(theme) {
    const effective = getEffectiveTheme(theme);
    const link = document.getElementById('hljs-theme');
    if (link) {
        link.href = HLJS_THEMES[effective];
    }
    if (typeof hljs !== 'undefined') {
        document.querySelectorAll('.triple-quote').forEach(function (el) {
            if (el.classList.length > 1) {
                hljs.highlightElement(el, { language: el.classList[1] });
            } else {
                hljs.highlightElement(el);
            }
            el.classList.remove('hljs');
        });
    }
}

const themes = ['auto', 'light', 'dark'];
let currentThemeIndex = 0;

// Get the theme from localStorage or default to 'auto'
const savedTheme = localStorage.getItem('theme') || 'auto';
document.documentElement.setAttribute('data-theme', savedTheme);
currentThemeIndex = themes.indexOf(savedTheme);

updateThemeToggle(themes[currentThemeIndex]);
updateHljsTheme(savedTheme);

// React to OS theme changes when in auto mode
window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', () => {
    if (document.documentElement.getAttribute('data-theme') === 'auto') {
        updateHljsTheme('auto');
    }
});

// Theme toggle click handler
const themeToggle = document.getElementById('theme-toggle');
themeToggle.addEventListener('click', () => {
    currentThemeIndex = (currentThemeIndex + 1) % themes.length;
    const newTheme = themes[currentThemeIndex];
    document.documentElement.setAttribute('data-theme', newTheme);
    localStorage.setItem('theme', newTheme);
    updateThemeToggle(newTheme);
    updateHljsTheme(newTheme);
});
