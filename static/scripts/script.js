// static/scripts/script.js - общие функции для всех страниц

// Глобальная переменная для URL обновления капчи
window.captchaRefreshUrl = null;

// Функция для установки URL обновления капчи
window.setCaptchaRefreshUrl = function(url) {
    window.captchaRefreshUrl = url;
}

// Универсальная функция для обновления капчи
window.refreshCaptcha = function() {
    
    // Если URL не установлен, пробуем получить из data-атрибута кнопки
    if (!window.captchaRefreshUrl) {
        const refreshBtn = document.querySelector('.btn-refresh-captcha');
        if (refreshBtn && refreshBtn.dataset.refreshUrl) {
            window.captchaRefreshUrl = refreshBtn.dataset.refreshUrl;
        } else {
            return;
        }
    }
    
    fetch(window.captchaRefreshUrl, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        }
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.json();
    })
    .then(data => {
        if (data.captcha_image) {
            const captchaImg = document.getElementById('captchaImg');
            if (captchaImg) {
                captchaImg.src = 'data:image/png;base64,' + data.captcha_image;
            }
            const captchaInput = document.getElementById('captcha');
            if (captchaInput) {
                captchaInput.value = '';
            }
        }
    })
    .catch(error => {
        console.error('Ошибка при обновлении капчи:', error);
        // Показываем сообщение об ошибке пользователю
        const captchaContainer = document.querySelector('.captcha-container');
        if (captchaContainer) {
            let errorMsg = captchaContainer.querySelector('.captcha-error-msg');
            if (!errorMsg) {
                errorMsg = document.createElement('div');
                errorMsg.className = 'alert alert-danger captcha-error-msg';
                errorMsg.style.fontSize = '12px';
                errorMsg.style.marginTop = '5px';
                errorMsg.style.padding = '5px';
                captchaContainer.appendChild(errorMsg);
            }
            errorMsg.textContent = '❌ Не удалось обновить капчу. Попробуйте обновить страницу.';
            setTimeout(() => {
                if (errorMsg && errorMsg.remove) {
                    errorMsg.remove();
                }
            }, 3000);
        }
    });
}

// Автоматическая очистка flash-сообщений через 5 секунд
window.autoClearFlashes = function() {
    setTimeout(function() {
        var flashes = document.querySelectorAll('.alert');
        flashes.forEach(function(flash) {
            if (!flash.innerHTML.includes('блокирован') && 
                !flash.innerHTML.includes('задержка') &&
                !flash.classList.contains('captcha-error-msg')) {
                flash.style.opacity = '0';
                setTimeout(function() {
                    if (flash && flash.remove) {
                        flash.remove();
                    }
                }, 500);
            }
        });
    }, 5000);
}

// Функция для запуска таймера обратного отсчета при блокировке
window.startCountdown = function(waitTime) {
    let remainingTime = waitTime;
    const countdownInterval = setInterval(function() {
        if (remainingTime <= 0) {
            clearInterval(countdownInterval);
            location.reload();
        } else {
            const alerts = document.querySelectorAll('.alert-main');
            alerts.forEach(function(alert) {
                if (alert.innerHTML.includes('блокирован')) {
                    alert.innerHTML = '⏱️ Внимание! Доступ временно заблокирован на ' + remainingTime + ' секунд из-за нескольких неудачных попыток.';
                }
            });
            remainingTime--;
        }
    }, 1000);
}

// Инициализация общих функций при загрузке страницы
document.addEventListener('DOMContentLoaded', function() {
    window.autoClearFlashes();
});