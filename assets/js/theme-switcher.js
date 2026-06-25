const HLJS_BASE = 'https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.11.1/styles/';

function isDarkTheme(theme) {
    if (theme === 'dark') {
        return true;
    }
    if (theme === 'light') {
        return false;
    }
    return window.matchMedia('(prefers-color-scheme: dark)').matches;
}

function updateHljsTheme(theme) {
    const link = document.getElementById('hljs-theme');
    if (!link) {
        return;
    }
  link.href = HLJS_BASE + (isDarkTheme(theme) ? 'atom-one-dark.min.css' : 'atom-one-light.min.css');
}

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

const themes = ['auto', 'light', 'dark'];
let currentThemeIndex = 0;

const savedTheme = localStorage.getItem('theme') || 'auto';
document.documentElement.setAttribute('data-theme', savedTheme);
currentThemeIndex = themes.indexOf(savedTheme);

updateThemeToggle(themes[currentThemeIndex]);
updateHljsTheme(savedTheme);

const themeToggle = document.getElementById('theme-toggle');
themeToggle.addEventListener('click', () => {
    currentThemeIndex = (currentThemeIndex + 1) % themes.length;
    const newTheme = themes[currentThemeIndex];
    document.documentElement.setAttribute('data-theme', newTheme);
    localStorage.setItem('theme', newTheme);
    updateThemeToggle(newTheme);
    updateHljsTheme(newTheme);
});

window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', () => {
    if (document.documentElement.getAttribute('data-theme') === 'auto') {
        updateHljsTheme('auto');
    }
});
