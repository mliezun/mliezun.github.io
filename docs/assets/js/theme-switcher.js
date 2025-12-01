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

const themes = ['auto', 'light', 'dark'];
let currentThemeIndex = 0;

// Get the theme from localStorage or default to 'auto'
const savedTheme = localStorage.getItem('theme') || 'auto';
document.documentElement.setAttribute('data-theme', savedTheme);
currentThemeIndex = themes.indexOf(savedTheme);

updateThemeToggle(themes[currentThemeIndex]);

// Theme toggle click handler
const themeToggle = document.getElementById('theme-toggle');
themeToggle.addEventListener('click', () => {
    currentThemeIndex = (currentThemeIndex + 1) % themes.length;
    const newTheme = themes[currentThemeIndex];
    document.documentElement.setAttribute('data-theme', newTheme);
    localStorage.setItem('theme', newTheme);
    updateThemeToggle(newTheme);
});
