window.showToast = function (msg, type) {
    const container = document.getElementById('toast-container');
    if (!container) return;
    const toast = document.createElement('div');
    toast.className = 'toast ' + (type || 'info');
    toast.innerText = msg;
    container.appendChild(toast);
    setTimeout(() => {
        toast.style.opacity = 0;
        setTimeout(() => container.removeChild(toast), 500);
    }, 2500);
};

// Theme switching
const THEMES = ['theme-light', 'theme-dark', 'theme-neon', 'theme-glass'];
const themeToggle = document.getElementById('theme-toggle');
function setTheme(theme) {
    document.body.classList.remove(...THEMES);
    document.body.classList.add(theme);
    localStorage.setItem('theme', theme);
}
if (themeToggle) {
    themeToggle.onclick = function () {
        let current = THEMES.findIndex(t => document.body.classList.contains(t));
        let next = (current + 1) % THEMES.length;
        setTheme(THEMES[next]);
    };
    // On load, set theme if previously chosen
    const saved = localStorage.getItem('theme');
    setTheme(saved && THEMES.includes(saved) ? saved : THEMES[0]);
}

// Animate progress bar fill
window.addEventListener('DOMContentLoaded', () => {
    const bar = document.querySelector('.progress-bar-inner');
    if (bar) {
        const width = bar.style.width;
        bar.style.width = '0';
        setTimeout(() => { bar.style.width = width; }, 100);
    }
    // Animate new tasks
    document.querySelectorAll('.todo-item').forEach(li => {
        li.classList.add('animated-in');
        setTimeout(() => li.classList.remove('animated-in'), 600);
    });
});

// Animate task completion (fade/slide)
document.querySelectorAll('.complete-btn').forEach(btn => {
    btn.addEventListener('click', function (e) {
        const li = btn.closest('.todo-item');
        if (li) {
            li.style.transform = 'translateX(40px) scale(0.95)';
            li.style.opacity = '0.2';
        }
    });
});

// Animate task removal (delete)
document.querySelectorAll('.delete-btn').forEach(btn => {
    btn.addEventListener('click', function (e) {
        const li = btn.closest('.todo-item');
        if (li) {
            li.classList.add('removing');
        }
    });
}); 