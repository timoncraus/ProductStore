// static/scripts/login.js - только специфичные для логина функции

// Проверяем, что функция setCaptchaRefreshUrl существует
if (typeof window.setCaptchaRefreshUrl === 'undefined') {
    console.error('setCaptchaRefreshUrl is not defined! Make sure script.js is loaded first.');
} else {
    // Устанавливаем URL для обновления капчи
    if (typeof refreshCaptchaUrl !== 'undefined') {
        window.setCaptchaRefreshUrl(refreshCaptchaUrl);
    }
}

// Инициализация страницы логина
document.addEventListener('DOMContentLoaded', function() {
    
    // Если есть блокировка, запускаем таймер
    if (typeof waitTime !== 'undefined' && waitTime > 0) {
        if (typeof window.startCountdown === 'function') {
            window.startCountdown(waitTime);
        } else {
            console.error('startCountdown function is not defined');
        }
    }
});