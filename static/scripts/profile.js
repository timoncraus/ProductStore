// Переключение вкладок
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

// ========== АВТОДОПОЛНЕНИЕ ДЛЯ АДРЕСОВ ==========

// Глобальные переменные для хранения выбранных ID
let selectedCountryId = null;
let selectedRegionId = null;
let selectedCityId = null;
let selectedStreetId = null;

// Функция для поиска с задержкой (debounce)
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Универсальная функция для автодополнения
function setupAutocomplete(inputId, hiddenId, suggestionsId, apiUrl, getParentId, onSelect) {
    const input = document.getElementById(inputId);
    const hidden = document.getElementById(hiddenId);
    const suggestions = document.getElementById(suggestionsId);
    
    if (!input || !hidden || !suggestions) return;
    
    const searchFunction = debounce(async () => {
        const query = input.value.trim();
        
        if (query.length < 2) {
            suggestions.style.display = 'none';
            return;
        }
        
        // Получаем ID родителя (если есть)
        let parentId = null;
        if (getParentId) {
            parentId = getParentId();
        }
        
        try {
            let url = `${apiUrl}?q=${encodeURIComponent(query)}`;
            if (parentId) {
                url += `&${inputId === 'regionInput' ? 'country_id' : 
                           inputId === 'cityInput' ? 'region_id' : 
                           inputId === 'streetInput' ? 'city_id' : ''}=${parentId}`;
            }
            
            const response = await fetch(url);
            const data = await response.json();
            
            if (data.length === 0) {
                suggestions.style.display = 'none';
                return;
            }
            
            suggestions.innerHTML = data.map(item => 
                `<div class="suggestion-item" data-id="${item.id}" data-name="${item.name}">
                    ${item.name}
                </div>`
            ).join('');
            suggestions.style.display = 'block';
            
            // Добавляем обработчики на подсказки
            document.querySelectorAll(`#${suggestionsId} .suggestion-item`).forEach(el => {
                el.addEventListener('click', () => {
                    input.value = el.dataset.name;
                    hidden.value = el.dataset.id;
                    suggestions.style.display = 'none';
                    
                    // Сохраняем ID в глобальную переменную
                    if (inputId === 'countryInput') {
                        selectedCountryId = parseInt(el.dataset.id);
                        // Активируем поле региона
                        const regionInput = document.getElementById('regionInput');
                        if (regionInput) {
                            regionInput.disabled = false;
                            regionInput.value = '';
                            document.getElementById('regionId').value = '';
                            selectedRegionId = null;
                        }
                        // Очищаем следующие поля
                        clearCityAndStreet();
                    } else if (inputId === 'regionInput') {
                        selectedRegionId = parseInt(el.dataset.id);
                        // Активируем поле города
                        const cityInput = document.getElementById('cityInput');
                        if (cityInput) {
                            cityInput.disabled = false;
                            cityInput.value = '';
                            document.getElementById('cityId').value = '';
                            selectedCityId = null;
                        }
                        // Очищаем улицу
                        clearStreet();
                    } else if (inputId === 'cityInput') {
                        selectedCityId = parseInt(el.dataset.id);
                        // Активируем поле улицы
                        const streetInput = document.getElementById('streetInput');
                        if (streetInput) {
                            streetInput.disabled = false;
                            streetInput.value = '';
                            document.getElementById('streetId').value = '';
                            selectedStreetId = null;
                        }
                    } else if (inputId === 'streetInput') {
                        selectedStreetId = parseInt(el.dataset.id);
                    }
                    
                    if (onSelect) onSelect(el.dataset.id);
                });
            });
        } catch (error) {
            console.error('Ошибка поиска:', error);
            suggestions.style.display = 'none';
        }
    }, 300);
    
    input.addEventListener('input', searchFunction);
    
    // Скрываем подсказки при клике вне
    document.addEventListener('click', (e) => {
        if (!suggestions.contains(e.target) && e.target !== input) {
            suggestions.style.display = 'none';
        }
    });
}

// Очистка полей города и улицы
function clearCityAndStreet() {
    const cityInput = document.getElementById('cityInput');
    if (cityInput) {
        cityInput.disabled = true;
        cityInput.value = '';
        document.getElementById('cityId').value = '';
        selectedCityId = null;
    }
    clearStreet();
}

// Очистка поля улицы
function clearStreet() {
    const streetInput = document.getElementById('streetInput');
    if (streetInput) {
        streetInput.disabled = true;
        streetInput.value = '';
        document.getElementById('streetId').value = '';
        selectedStreetId = null;
    }
}

// Настройка автодополнения
function initAddressAutocomplete() {
    // Поиск страны
    setupAutocomplete(
        'countryInput', 'countryId', 'countrySuggestions', '/api/search-country',
        null,
        (id) => { selectedCountryId = parseInt(id); }
    );
    
    // Поиск региона (зависит от выбранной страны)
    setupAutocomplete(
        'regionInput', 'regionId', 'regionSuggestions', '/api/search-region',
        () => selectedCountryId,
        (id) => { selectedRegionId = parseInt(id); }
    );
    
    // Поиск города (зависит от выбранного региона)
    setupAutocomplete(
        'cityInput', 'cityId', 'citySuggestions', '/api/search-city',
        () => selectedRegionId,
        (id) => { selectedCityId = parseInt(id); }
    );
    
    // Поиск улицы (зависит от выбранного города)
    setupAutocomplete(
        'streetInput', 'streetId', 'streetSuggestions', '/api/search-street',
        () => selectedCityId,
        (id) => { selectedStreetId = parseInt(id); }
    );
}

// Показать/скрыть форму добавления адреса
function initAddressFormControls() {
    const showBtn = document.getElementById('showAddAddressBtn');
    const addForm = document.getElementById('addAddressForm');
    const cancelBtn = document.getElementById('cancelAddAddress');
    
    if (showBtn && addForm) {
        showBtn.addEventListener('click', () => {
            addForm.style.display = 'block';
            showBtn.style.display = 'none';
            // Инициализируем автодополнение при показе формы
            setTimeout(initAddressAutocomplete, 100);
        });
    }
    
    if (cancelBtn && addForm) {
        cancelBtn.addEventListener('click', () => {
            addForm.style.display = 'none';
            if (showBtn) showBtn.style.display = 'inline-block';
            
            // Очищаем форму
            const form = document.getElementById('addressForm');
            if (form) form.reset();
            
            // Очищаем скрытые поля
            document.getElementById('countryId').value = '';
            document.getElementById('regionId').value = '';
            document.getElementById('cityId').value = '';
            document.getElementById('streetId').value = '';
            
            // Сбрасываем глобальные переменные
            selectedCountryId = null;
            selectedRegionId = null;
            selectedCityId = null;
            selectedStreetId = null;
            
            // Отключаем поля
            const regionInput = document.getElementById('regionInput');
            if (regionInput) regionInput.disabled = true;
            const cityInput = document.getElementById('cityInput');
            if (cityInput) cityInput.disabled = true;
            const streetInput = document.getElementById('streetInput');
            if (streetInput) streetInput.disabled = true;
        });
    }
}

// Инициализация при загрузке страницы
document.addEventListener('DOMContentLoaded', () => {
    initAddressFormControls();
    
    // Если форма адреса уже видна (например, при ошибке валидации)
    const addForm = document.getElementById('addAddressForm');
    if (addForm && addForm.style.display === 'block') {
        initAddressAutocomplete();
    }
});