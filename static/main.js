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

// Dark mode toggle
const darkToggle = document.getElementById('dark-toggle');
if (darkToggle) {
    darkToggle.onclick = function () {
        document.body.classList.toggle('dark');
        localStorage.setItem('darkMode', document.body.classList.contains('dark'));
    };
    // On load, set dark mode if previously chosen
    if (localStorage.getItem('darkMode') === 'true') {
        document.body.classList.add('dark');
    }
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