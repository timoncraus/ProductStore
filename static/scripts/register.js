// static/scripts/register.js - только специфичные для регистрации функции

// Функция для проверки сложности пароля в реальном времени
function checkPasswordStrength(password) {
    const checks = {
        length: password.length >= 9,
        letters: /[A-Za-z]/.test(password),
        digits: /\d/.test(password),
        special: /[!@#$%^&*(),.?":{}|_\-+=]/.test(password)
    };
    
    const strength = Object.values(checks).filter(Boolean).length;
    
    // Обновляем индикатор
    const strengthIndicator = document.getElementById('password-strength');
    if (strengthIndicator) {
        const strengthTexts = ['Очень слабый', 'Слабый', 'Средний', 'Хороший', 'Отличный'];
        const strengthColors = ['#dc3545', '#fd7e14', '#ffc107', '#20c997', '#28a745'];
        
        strengthIndicator.textContent = `Сложность пароля: ${strengthTexts[strength]}`;
        strengthIndicator.style.color = strengthColors[strength];
        
        // Добавляем детали
        let details = [];
        if (!checks.length) details.push('минимум 9 символов');
        if (!checks.letters) details.push('буквы');
        if (!checks.digits) details.push('цифры');
        if (!checks.special) details.push('спецсимволы');
        
        if (details.length > 0) {
            strengthIndicator.innerHTML = `Сложность пароля: ${strengthTexts[strength]}<br>
            <small style="font-size: 10px;">Требуется: ${details.join(', ')}</small>`;
        } else {
            strengthIndicator.innerHTML = `Сложность пароля: ${strengthTexts[strength]}`;
        }
    }
    
    return checks;
}

// Функция для валидации формы регистрации
function validateRegistrationForm(event) {
    const password = document.getElementById('password').value;
    const password2 = document.getElementById('password2').value;
    const username = document.getElementById('username').value;
    const email = document.getElementById('email').value;
    const phone = document.getElementById('phone').value;
    const captcha = document.getElementById('captcha').value;
    
    const passwordChecks = checkPasswordStrength(password);
    const errors = [];
    
    // Проверка имени пользователя
    if (!username || username.length < 3) {
        errors.push('Имя пользователя должно содержать минимум 3 символа');
    }
    
    // Проверка email
    const emailPattern = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
    if (!emailPattern.test(email)) {
        errors.push('Неверный формат email');
    }
    
    // Проверка телефона
    const phonePattern = /^(\+7|8|7)?[\s\-]?\(?[0-9]{3}\)?[\s\-]?[0-9]{3}[\s\-]?[0-9]{2}[\s\-]?[0-9]{2}$/;
    if (!phonePattern.test(phone.replace(/[\s\-\(\)]/g, ''))) {
        errors.push('Неверный формат телефона');
    }
    
    // Проверка пароля
    if (!passwordChecks.length) {
        errors.push('Пароль должен содержать минимум 9 символов');
    }
    if (!passwordChecks.letters) {
        errors.push('Пароль должен содержать буквы');
    }
    if (!passwordChecks.digits) {
        errors.push('Пароль должен содержать цифры');
    }
    if (!passwordChecks.special) {
        errors.push('Пароль должен содержать спецсимволы');
    }
    
    // Проверка совпадения паролей
    if (password !== password2) {
        errors.push('Пароли не совпадают');
    }
    
    // Проверка капчи
    if (!captcha) {
        errors.push('Введите код с картинки');
    }
    
    // Если есть ошибки, показываем их и отменяем отправку
    if (errors.length > 0) {
        event.preventDefault();
        alert('Пожалуйста, исправьте следующие ошибки:\n\n' + errors.join('\n'));
        return false;
    }
    
    return true;
}

// Проверяем, что функция setCaptchaRefreshUrl существует
if (typeof window.setCaptchaRefreshUrl === 'undefined') {
    console.error('setCaptchaRefreshUrl is not defined! Make sure script.js is loaded first.');
} else {
    // Устанавливаем URL для обновления капчи
    if (typeof refreshCaptchaUrl !== 'undefined') {
        window.setCaptchaRefreshUrl(refreshCaptchaUrl);
    }
}

// Инициализация страницы регистрации
document.addEventListener('DOMContentLoaded', function() {
    
    // Назначаем обработчик для кнопки обновления капчи
    const refreshBtn = document.getElementById('refreshCaptchaBtn');
    if (refreshBtn) {
        // Если кнопка есть, устанавливаем обработчик
        refreshBtn.addEventListener('click', function(e) {
            e.preventDefault();
            if (typeof window.refreshCaptcha === 'function') {
                window.refreshCaptcha();
            } else {
                console.error('refreshCaptcha function is not defined');
            }
        });
    }
    
    // Назначаем обработчик для формы регистрации
    const registerForm = document.getElementById('registerForm');
    if (registerForm) {
        registerForm.addEventListener('submit', validateRegistrationForm);
    }
    
    // Добавляем индикатор сложности пароля
    const passwordInput = document.getElementById('password');
    if (passwordInput && !document.getElementById('password-strength')) {
        const strengthDiv = document.createElement('div');
        strengthDiv.id = 'password-strength';
        strengthDiv.className = 'password-strength-indicator';
        strengthDiv.style.marginTop = '8px';
        strengthDiv.style.fontSize = '12px';
        strengthDiv.style.fontWeight = 'bold';
        passwordInput.parentNode.insertBefore(strengthDiv, passwordInput.nextSibling);
        
        passwordInput.addEventListener('input', function() {
            checkPasswordStrength(this.value);
        });
    }
});