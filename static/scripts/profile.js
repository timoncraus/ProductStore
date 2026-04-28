document.querySelectorAll('.tab-btn').forEach(btn => {
    btn.addEventListener('click', () => {
        const tabId = btn.dataset.tab;
        document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
        document.querySelectorAll('.tab-content').forEach(t => t.classList.remove('active'));
        btn.classList.add('active');
        document.getElementById(`tab-${tabId}`).classList.add('active');
        
        // Сохраняем активную вкладку в localStorage
        localStorage.setItem('activeProfileTab', tabId);
    });
});

// Восстанавливаем активную вкладку при загрузке
const savedTab = localStorage.getItem('activeProfileTab');
if (savedTab) {
    const tabToActivate = document.querySelector(`.tab-btn[data-tab="${savedTab}"]`);
    if (tabToActivate) {
        tabToActivate.click();
    }
}

// Валидация телефона на клиенте
document.querySelectorAll('input[type="tel"]').forEach(input => {
    input.addEventListener('input', function(e) {
        let value = this.value.replace(/[\s\-\(\)]/g, '');
        if (value.startsWith('8') || value.startsWith('7') || value.startsWith('+7')) {
            this.style.borderColor = 'var(--primary)';
        } else if (value.length > 0) {
            this.style.borderColor = 'var(--danger)';
        } else {
            this.style.borderColor = '';
        }
    });
});