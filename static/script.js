// Добавление в корзину через AJAX
function addToCart(productId, sizeId, quantity) {
  fetch("/cart/add", {
    method: "POST",
    headers: {
      "Content-Type": "application/x-www-form-urlencoded",
    },
    body: `product_id=${productId}&size_id=${sizeId}&quantity=${quantity}`,
  })
    .then((response) => response.json())
    .then((data) => {
      if (data.success) {
        updateCartCount();
        showNotification("Товар добавлен в корзину", "success");
      }
    });
}

// Обновление счетчика корзины
function updateCartCount() {
  fetch("/api/cart/count")
    .then((response) => response.json())
    .then((data) => {
      const cartBadge = document.querySelector(".cart-count");
      if (cartBadge) {
        cartBadge.textContent = data.count;
      }
    });
}

// Валидация формы
function validateForm(formId) {
  const form = document.getElementById(formId);
  if (!form) return true;

  const password = form.querySelector('[name="password"]');
  const password2 = form.querySelector('[name="password2"]');

  if (password && password2 && password.value !== password2.value) {
    alert("Пароли не совпадают");
    return false;
  }

  const phone = form.querySelector('[name="phone"]');
  if (phone) {
    const phoneRegex =
      /^(\+7|8|7)?[\s\-]?\(?[0-9]{3}\)?[\s\-]?[0-9]{3}[\s\-]?[0-9]{2}[\s\-]?[0-9]{2}$/;
    if (!phoneRegex.test(phone.value)) {
      alert("Введите корректный номер телефона");
      return false;
    }
  }

  return true;
}

// Уведомления
function showNotification(message, type) {
  const notification = document.createElement("div");
  notification.className = `alert alert-${type}`;
  notification.textContent = message;
  notification.style.position = "fixed";
  notification.style.top = "20px";
  notification.style.right = "20px";
  notification.style.zIndex = "9999";
  document.body.appendChild(notification);

  setTimeout(() => {
    notification.remove();
  }, 3000);
}

// Подтверждение удаления
function confirmDelete(message) {
  return confirm(message || "Вы уверены, что хотите удалить эту запись?");
}

// Поиск с автодополнением
function initSearchAutocomplete() {
  const searchInput = document.querySelector(".search-autocomplete");
  if (!searchInput) return;

  searchInput.addEventListener("input", function () {
    const query = this.value;
    if (query.length < 2) return;

    fetch(`/api/search?q=${encodeURIComponent(query)}`)
      .then((response) => response.json())
      .then((data) => {
        const suggestions = document.querySelector(".search-suggestions");
        if (suggestions) {
          suggestions.innerHTML = data
            .map(
              (item) =>
                `<div class="suggestion" data-id="${item.id}">${item.name} - ${item.price}₽</div>`,
            )
            .join("");
        }
      });
  });
}

// Загрузка размеров для товара
function loadSizes(productId) {
  fetch(`/api/product/${productId}/sizes`)
    .then((response) => response.json())
    .then((data) => {
      const sizeSelect = document.querySelector("#size-select");
      if (sizeSelect) {
        sizeSelect.innerHTML = data
          .map(
            (size) =>
              `<option value="${size.id}">${size.name} (${size.stock_quantity} шт.)</option>`,
          )
          .join("");
      }
    });
}

// Инициализация при загрузке страницы
document.addEventListener("DOMContentLoaded", function () {
  initSearchAutocomplete();
  updateCartCount();

  // Подтверждение удаления для всех кнопок delete
  document.querySelectorAll(".btn-delete").forEach((btn) => {
    btn.addEventListener("click", function (e) {
      if (!confirmDelete()) {
        e.preventDefault();
      }
    });
  });
});


// Ждем полной загрузки DOM
document.addEventListener('DOMContentLoaded', function() {
    // Находим все кнопки вкладок
    const tabBtns = document.querySelectorAll('.tab-btn');
    
    tabBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            // Получаем ID вкладки из data-tab атрибута
            const tabId = this.getAttribute('data-tab');
            
            // Убираем active класс у всех кнопок
            tabBtns.forEach(b => b.classList.remove('active'));
            
            // Добавляем active класс текущей кнопке
            this.classList.add('active');
            
            // Скрываем все содержимое вкладок
            document.querySelectorAll('.tab-content').forEach(content => {
                content.classList.remove('active');
            });
            
            // Показываем выбранную вкладку
            const activeTab = document.getElementById(`tab-${tabId}`);
            if (activeTab) {
                activeTab.classList.add('active');
            }
        });
    });
});
