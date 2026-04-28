-- =====================================================
-- КУРСОВАЯ РАБОТА: Продуктовые товары
-- УПРОЩЕННАЯ НОРМАЛИЗОВАННАЯ БД (9 ТАБЛИЦ)
-- =====================================================

DROP DATABASE IF EXISTS product_store;
CREATE DATABASE product_store;
USE product_store;

-- =====================================================
-- 1. ПОЛЬЗОВАТЕЛИ
-- =====================================================
CREATE TABLE user (
    id INT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    phone VARCHAR(20) NOT NULL,
    full_name VARCHAR(200),
    role ENUM('admin', 'user') DEFAULT 'user',
    address TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP NULL,
    is_active BOOLEAN DEFAULT TRUE
);

-- =====================================================
-- 2. КАТЕГОРИИ ТОВАРОВ (ИЕРАРХИЧЕСКИЕ)
-- =====================================================
CREATE TABLE category (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL,
    slug VARCHAR(100) UNIQUE NOT NULL,
    description TEXT,
    image_url VARCHAR(500),
    parent_id INT NULL,
    sort_order INT DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    FOREIGN KEY (parent_id) REFERENCES category(id)
);

-- =====================================================
-- 3. ТОВАРЫ
-- =====================================================
CREATE TABLE product (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(200) NOT NULL,
    slug VARCHAR(200) UNIQUE NOT NULL,
    description TEXT,
    price DECIMAL(10,2) NOT NULL,
    old_price DECIMAL(10,2),
    image_url VARCHAR(500),
    category_id INT NOT NULL,
    stock INT DEFAULT 0,
    unit VARCHAR(20) DEFAULT 'шт',
    rating DECIMAL(3,2) DEFAULT 0,
    sales_count INT DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    is_new BOOLEAN DEFAULT FALSE,
    is_hit BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (category_id) REFERENCES category(id)
);

-- =====================================================
-- 4. ЗАКАЗЫ
-- =====================================================
CREATE TABLE order_status (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(50) UNIQUE NOT NULL
);

CREATE TABLE orders (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    order_number VARCHAR(50) UNIQUE NOT NULL,
    total_amount DECIMAL(10,2) NOT NULL,
    delivery_address TEXT NOT NULL,
    recipient_name VARCHAR(200),
    recipient_phone VARCHAR(20),
    comment TEXT,
    status_id INT DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES user(id),
    FOREIGN KEY (status_id) REFERENCES order_status(id)
);

-- =====================================================
-- 5. ТОВАРЫ В ЗАКАЗЕ
-- =====================================================
CREATE TABLE order_item (
    id INT PRIMARY KEY AUTO_INCREMENT,
    order_id INT NOT NULL,
    product_id INT NOT NULL,
    product_name VARCHAR(200) NOT NULL,
    quantity INT NOT NULL,
    price DECIMAL(10,2) NOT NULL,
    FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES product(id)
);

-- =====================================================
-- 6. КОРЗИНА
-- =====================================================
CREATE TABLE cart (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES user(id) ON DELETE CASCADE
);

CREATE TABLE cart_item (
    id INT PRIMARY KEY AUTO_INCREMENT,
    cart_id INT NOT NULL,
    product_id INT NOT NULL,
    quantity INT NOT NULL DEFAULT 1,
    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (cart_id) REFERENCES cart(id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES product(id),
    UNIQUE KEY unique_cart_product (cart_id, product_id)
);

-- =====================================================
-- 7. ИЗБРАННОЕ
-- =====================================================
CREATE TABLE wishlist (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    product_id INT NOT NULL,
    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES user(id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES product(id) ON DELETE CASCADE,
    UNIQUE KEY unique_wishlist (user_id, product_id)
);

-- =====================================================
-- НАЧАЛЬНЫЕ ДАННЫЕ
-- =====================================================

-- Админ (пароль: Admin123! - хэш: 8d969eef6ecad3c29a3a629280e686cf0c3f5d5a86aff3ca12020c923adc6c92)
INSERT INTO user (username, email, phone, password_hash, full_name, role) VALUES
('admin', 'admin@example.com', '+79990000000', '8d969eef6ecad3c29a3a629280e686cf0c3f5d5a86aff3ca12020c923adc6c92', 'Администратор', 'admin');

-- Обычные пользователи
INSERT INTO user (username, email, phone, password_hash, full_name) VALUES
('ivan', 'ivan@mail.ru', '+79123456789', '8d969eef6ecad3c29a3a629280e686cf0c3f5d5a86aff3ca12020c923adc6c92', 'Иван Петров'),
('maria', 'maria@mail.ru', '+79234567890', '8d969eef6ecad3c29a3a629280e686cf0c3f5d5a86aff3ca12020c923adc6c92', 'Мария Сидорова');

-- Статусы заказов
INSERT INTO order_status (name) VALUES ('Новый'), ('Подтвержден'), ('Оплачен'), ('Отправлен'), ('Доставлен'), ('Отменен');

-- Категории товаров
INSERT INTO category (id, name, slug, image_url, parent_id, sort_order) VALUES
(1, 'Бакалея', 'grocery', '/static/images/categories/grocery.jpg', NULL, 1),
(2, 'Молочные продукты', 'dairy', '/static/images/categories/dairy.jpg', NULL, 2),
(3, 'Мясо и птица', 'meat', '/static/images/categories/meat.jpg', NULL, 3),
(4, 'Овощи и фрукты', 'vegetables-fruits', '/static/images/categories/vegetables-fruits.jpg', NULL, 4),
(5, 'Напитки', 'beverages', '/static/images/categories/beverages.jpg', NULL, 5),
(6, 'Кондитерские изделия', 'confectionery', '/static/images/categories/confectionery.jpg', NULL, 6),
(7, 'Хлеб и выпечка', 'bread', '/static/images/categories/bread.jpg', NULL, 7),
(8, 'Полуфабрикаты', 'ready-meals', '/static/images/categories/ready-meals.jpg', NULL, 8);

-- Товары
INSERT INTO product (id, name, slug, description, price, old_price, image_url, category_id, stock, unit, rating, sales_count, is_new, is_hit) VALUES
-- Бакалея (1-8)
(1, 'Гречневая крупа "Мистраль"', 'buckwheat', 'Ядрица высшего сорта. Быстро варится, рассыпчатая.', 89.90, 109.90, '/static/images/products/buckwheat.jpg', 1, 500, 'кг', 4.8, 1800, FALSE, TRUE),
(2, 'Рис "Басмати"', 'basmati-rice', 'Длиннозерный рис с ароматом. Идеален для плова.', 159.90, 189.90, '/static/images/products/rice.jpg', 1, 300, 'кг', 4.6, 980, FALSE, TRUE),
(3, 'Овсяные хлопья "Геркулес"', 'oat-flakes', 'Классические овсяные хлопья для здорового завтрака.', 79.90, 99.90, '/static/images/products/oatmeal.jpg', 1, 400, 'кг', 4.5, 2340, FALSE, FALSE),
(4, 'Макароны Barilla Спагетти', 'barilla-spaghetti', 'Спагетти из твердых сортов пшеницы.', 129.90, NULL, '/static/images/products/pasta.jpg', 1, 200, 'уп', 4.7, 3450, FALSE, TRUE),
(5, 'Мука пшеничная в/с', 'wheat-flour', 'Мука высшего сорта. 1 кг.', 59.90, NULL, '/static/images/products/flour.jpg', 1, 600, 'кг', 4.4, 1200, FALSE, FALSE),
(6, 'Сахар песок', 'sugar', 'Сахар-песок рафинированный.', 69.90, 79.90, '/static/images/products/sugar.jpg', 1, 800, 'кг', 4.5, 3400, FALSE, FALSE),
(7, 'Соль поваренная', 'salt', 'Соль поваренная пищевая. 1 кг.', 29.90, NULL, '/static/images/products/salt.jpg', 1, 1000, 'кг', 4.3, 2100, FALSE, FALSE),
(8, 'Масло подсолнечное', 'sunflower-oil', 'Рафинированное дезодорированное масло. 1 л.', 119.90, 139.90, '/static/images/products/oil.jpg', 1, 300, 'л', 4.7, 890, FALSE, FALSE),

-- Молочные продукты (9-15)
(9, 'Молоко 3.2% "Домик в деревне"', 'milk-32', 'Пастеризованное молоко. 1 л.', 89.90, 99.90, '/static/images/products/milk.jpg', 2, 500, 'л', 4.8, 5200, FALSE, TRUE),
(10, 'Кефир 2.5%', 'kefir', 'Натуральный кефир. 1 л.', 79.90, NULL, '/static/images/products/kefir.jpg', 2, 400, 'л', 4.6, 3100, FALSE, FALSE),
(11, 'Сметана 20%', 'sour-cream', 'Домашняя сметана. 400 г.', 129.90, 149.90, '/static/images/products/sour-cream.jpg', 2, 200, 'шт', 4.7, 2300, FALSE, FALSE),
(12, 'Творог 9%', 'cottage-cheese', 'Рассыпчатый творог. 500 г.', 159.90, 179.90, '/static/images/products/cottage-cheese.jpg', 2, 150, 'шт', 4.8, 1800, FALSE, TRUE),
(13, 'Сыр "Российский"', 'russian-cheese', 'Твердый сыр 50%. 200 г.', 179.90, 199.90, '/static/images/products/cheese.jpg', 2, 200, 'шт', 4.9, 890, FALSE, TRUE),
(14, 'Йогурт Activia натуральный', 'activia-yogurt', 'Натуральный йогурт. 125 г.', 75.00, 89.90, '/static/images/products/yogurt.jpg', 2, 1000, 'шт', 4.6, 3100, TRUE, FALSE),
(15, 'Масло сливочное 82.5%', 'butter', 'Крестьянское масло. 180 г.', 149.90, 169.90, '/static/images/products/butter.jpg', 2, 300, 'шт', 4.7, 2100, FALSE, FALSE),

-- Мясо и птица (16-21)
(16, 'Куриное филе охлажденное', 'chicken-fillet', 'Охлажденное куриное филе. 1 кг.', 349.90, 399.90, '/static/images/products/chicken.jpg', 3, 150, 'кг', 4.8, 1450, FALSE, TRUE),
(17, 'Куриные крылья', 'chicken-wings', 'Для гриля и запекания. 1 кг.', 249.90, NULL, '/static/images/products/wings.jpg', 3, 200, 'кг', 4.5, 1230, FALSE, FALSE),
(18, 'Говядина вырезка', 'beef-tenderloin', 'Нежная говяжья вырезка. 1 кг.', 899.00, 999.00, '/static/images/products/beef.jpg', 3, 80, 'кг', 4.9, 560, FALSE, TRUE),
(19, 'Фарш говяжий', 'beef-mince', 'Натуральный фарш 80/20. 1 кг.', 399.90, 449.90, '/static/images/products/mince.jpg', 3, 120, 'кг', 4.7, 1320, FALSE, FALSE),
(20, 'Фарш куриный', 'chicken-mince', 'Нежный куриный фарш. 1 кг.', 299.90, NULL, '/static/images/products/chicken-mince.jpg', 3, 100, 'кг', 4.6, 670, FALSE, FALSE),
(21, 'Свинина на кости', 'pork-bone', 'Для супа и жарки. 1 кг.', 349.90, 399.90, '/static/images/products/pork.jpg', 3, 90, 'кг', 4.5, 890, FALSE, FALSE),

-- Овощи и фрукты (22-27)
(22, 'Бананы', 'bananas', 'Спелые сладкие бананы. 1 кг.', 129.90, 149.90, '/static/images/products/bananas.jpg', 4, 300, 'кг', 4.6, 5400, FALSE, TRUE),
(23, 'Яблоки "Голден"', 'golden-apples', 'Сочные сладкие яблоки. 1 кг.', 119.90, 139.90, '/static/images/products/apples.jpg', 4, 250, 'кг', 4.7, 4900, FALSE, TRUE),
(24, 'Апельсины', 'oranges', 'Сочные апельсины. 1 кг.', 139.90, 159.90, '/static/images/products/oranges.jpg', 4, 200, 'кг', 4.5, 3800, FALSE, FALSE),
(25, 'Картофель', 'potatoes', 'Молодой картофель. 1 кг.', 59.90, 79.90, '/static/images/products/potatoes.jpg', 4, 800, 'кг', 4.3, 8900, FALSE, FALSE),
(26, 'Помидоры', 'tomatoes', 'Спелые помидоры. 1 кг.', 199.90, 249.90, '/static/images/products/tomatoes.jpg', 4, 150, 'кг', 4.6, 4500, FALSE, FALSE),
(27, 'Огурцы', 'cucumbers', 'Хрустящие огурцы. 1 кг.', 159.90, 199.90, '/static/images/products/cucumbers.jpg', 4, 180, 'кг', 4.5, 4300, FALSE, FALSE),

-- Напитки (28-33)
(28, 'Вода "Святой источник" 1.5л', 'holy-spring-water', 'Питьевая вода первой категории.', 49.90, 59.90, '/static/images/products/water.jpg', 5, 2000, 'шт', 4.5, 8600, FALSE, TRUE),
(29, 'Сок "Добрый" апельсиновый', 'dobry-juice', 'Сок прямого отжима. 1 л.', 129.90, 149.90, '/static/images/products/juice.jpg', 5, 800, 'шт', 4.4, 4800, FALSE, FALSE),
(30, 'Coca-Cola 0.5л', 'coca-cola', 'Классическая Coca-Cola.', 89.90, 99.90, '/static/images/products/cola.jpg', 5, 1500, 'шт', 4.7, 12900, FALSE, TRUE),
(31, 'Квас "Очаковский" 1.5л', 'ochakovsky-kvass', 'Натуральный квас брожения.', 129.90, 149.90, '/static/images/products/kvass.jpg', 5, 500, 'шт', 4.7, 3400, FALSE, FALSE),
(32, 'Чай Lipton чёрный', 'lipton-tea', 'Чай в пакетиках. 25 шт.', 159.90, 179.90, '/static/images/products/tea.jpg', 5, 300, 'уп', 4.6, 2100, FALSE, FALSE),
(33, 'Кофе Jacobs молотый', 'jacobs-coffee', 'Молотый кофе. 250 г.', 349.90, 399.90, '/static/images/products/coffee.jpg', 5, 200, 'шт', 4.8, 1560, TRUE, TRUE),

-- Кондитерские изделия (34-39)
(34, 'Шоколад Milka молочный', 'milka-chocolate', 'Молочный шоколад. 90 г.', 129.90, 149.90, '/static/images/products/chocolate.jpg', 6, 600, 'шт', 4.9, 6500, FALSE, TRUE),
(35, 'Печенье Oreo', 'oreo', 'Хрустящее печенье с кремом. 150 г.', 99.90, 119.90, '/static/images/products/oreo.jpg', 6, 800, 'шт', 4.8, 8700, FALSE, TRUE),
(36, 'Конфеты "Коровка"', 'korovka-candies', 'Молочные конфеты. 500 г.', 199.90, 249.90, '/static/images/products/candies.jpg', 6, 400, 'уп', 4.5, 3400, FALSE, FALSE),
(37, 'Пряники тульские', 'tula-gingerbread', 'Медовые пряники. 300 г.', 89.90, NULL, '/static/images/products/gingerbread.jpg', 6, 500, 'уп', 4.6, 2300, FALSE, FALSE),
(38, 'Вафли "Артек"', 'artek-waffles', 'Сливочные вафли. 200 г.', 79.90, 89.90, '/static/images/products/waffles.jpg', 6, 600, 'шт', 4.4, 2100, FALSE, FALSE),
(39, 'Зефир ванильный', 'vanilla-zephyr', 'Нежный зефир. 300 г.', 119.90, 139.90, '/static/images/products/zephyr.jpg', 6, 350, 'уп', 4.7, 1800, TRUE, FALSE),

-- Хлеб и выпечка (40-43)
(40, 'Хлеб "Бородинский"', 'borodinsky-bread', 'Ржаной хлеб с тмином.', 59.90, 69.90, '/static/images/products/borodinsky.jpg', 7, 400, 'шт', 4.8, 6500, FALSE, TRUE),
(41, 'Батон нарезной', 'white-bread', 'Пшеничный батон.', 49.90, 59.90, '/static/images/products/white-bread.jpg', 7, 600, 'шт', 4.6, 8900, FALSE, FALSE),
(42, 'Лаваш армянский', 'armenian-lavash', 'Тонкий лаваш. 300 г.', 39.90, 49.90, '/static/images/products/lavash.jpg', 7, 500, 'шт', 4.5, 5600, FALSE, FALSE),
(43, 'Булочка с маком', 'poppy-bun', 'Сдобная булочка.', 29.90, NULL, '/static/images/products/bun.jpg', 7, 700, 'шт', 4.4, 6700, FALSE, FALSE),

-- Полуфабрикаты (44-47)
(44, 'Пельмени "Сибирские"', 'siberian-dumplings', 'Домашние пельмени. 800 г.', 349.90, 399.90, '/static/images/products/dumplings.jpg', 8, 200, 'уп', 4.5, 1340, FALSE, FALSE),
(45, 'Вареники с картошкой', 'potato-varenyky', 'Вареники с картофелем. 800 г.', 249.90, 299.90, '/static/images/products/varenyky.jpg', 8, 180, 'уп', 4.4, 890, FALSE, FALSE),
(46, 'Пицца "Маргарита"', 'margherita-pizza', 'Замороженная пицца. 350 г.', 299.90, 349.90, '/static/images/products/pizza.jpg', 8, 150, 'шт', 4.4, 1230, FALSE, FALSE),
(47, 'Котлеты куриные', 'chicken-cutlets', 'Замороженные котлеты. 400 г.', 249.90, 299.90, '/static/images/products/cutlets.jpg', 8, 120, 'уп', 4.5, 890, FALSE, FALSE);

-- Корзины для пользователей
INSERT INTO cart (user_id) VALUES (2), (3);

-- Избранное
INSERT INTO wishlist (user_id, product_id) VALUES 
(2, 1), (2, 9), (2, 16), (2, 34),
(3, 4), (3, 13), (3, 22), (3, 30);

-- Тестовые заказы
INSERT INTO orders (user_id, order_number, total_amount, delivery_address, recipient_name, recipient_phone, status_id) VALUES
(2, 'ORD-20241201-0001', 518.80, 'г. Москва, ул. Тверская, д. 1, кв. 5', 'Иван Петров', '+79123456789', 4),
(3, 'ORD-20241201-0002', 548.70, 'г. Одинцово, ул. Ленина, д. 10, кв. 8', 'Мария Сидорова', '+79234567890', 3);

-- Товары в заказах
INSERT INTO order_item (order_id, product_id, product_name, quantity, price) VALUES
(1, 1, 'Гречневая крупа "Мистраль"', 1, 89.90),
(1, 9, 'Молоко 3.2% "Домик в деревне"', 1, 89.90),
(1, 34, 'Шоколад Milka молочный', 1, 129.90),
(2, 4, 'Макароны Barilla Спагетти', 1, 129.90),
(2, 13, 'Сыр "Российский"', 1, 179.90),
(2, 22, 'Бананы', 1, 129.90);

-- Создание индексов для оптимизации
CREATE INDEX idx_product_category ON product(category_id);
CREATE INDEX idx_product_price ON product(price);
CREATE INDEX idx_order_user ON orders(user_id);
CREATE INDEX idx_order_status ON orders(status_id);
CREATE INDEX idx_cart_user ON cart(user_id);
CREATE INDEX idx_wishlist_user ON wishlist(user_id);

-- Проверка
SELECT '=== БАЗА ДАННЫХ СОЗДАНА УСПЕШНО ===' AS message;
SELECT COUNT(*) as total_products FROM product;
SELECT c.name as category, COUNT(*) as products_count 
FROM product p 
JOIN category c ON p.category_id = c.id 
GROUP BY p.category_id;

ALTER TABLE cart_item ADD COLUMN price DECIMAL(10,2) NOT NULL DEFAULT 0;

-- =====================================================
-- АДРЕСНАЯ СИСТЕМА (НОРМАЛИЗОВАННАЯ)
-- =====================================================

-- Страны
CREATE TABLE country (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) UNIQUE NOT NULL,
    code VARCHAR(10)
);

-- Регионы/области
CREATE TABLE region (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL,
    country_id INT NOT NULL,
    FOREIGN KEY (country_id) REFERENCES country(id)
);

-- Населенные пункты (города, поселки, села)
CREATE TABLE city (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL,
    region_id INT NOT NULL,
    FOREIGN KEY (region_id) REFERENCES region(id)
);

-- Улицы
CREATE TABLE street (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL,
    city_id INT NOT NULL,
    FOREIGN KEY (city_id) REFERENCES city(id)
);

-- Адреса пользователей
CREATE TABLE user_address (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    street_id INT NOT NULL,
    house VARCHAR(20) NOT NULL,
    apartment VARCHAR(20),
    entrance VARCHAR(10),
    floor INT,
    postal_code VARCHAR(20),
    is_default BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES user(id) ON DELETE CASCADE,
    FOREIGN KEY (street_id) REFERENCES street(id)
);

-- Начальные данные для адресов
INSERT INTO country (name, code) VALUES ('Россия', 'RU'), ('Беларусь', 'BY'), ('Казахстан', 'KZ');

INSERT INTO region (name, country_id) VALUES 
('Московская область', 1),
('Москва', 1),
('Санкт-Петербург', 1),
('Ленинградская область', 1);

INSERT INTO city (name, region_id) VALUES 
('Москва', 2),
('Одинцово', 1),
('Санкт-Петербург', 3),
('Всеволожск', 4);

INSERT INTO street (name, city_id) VALUES 
('Тверская', 1),
('Арбат', 1),
('Ленина', 2),
('Невский проспект', 3);



-- Добавляем поле для картинок в таблицу product
ALTER TABLE product ADD COLUMN image_url VARCHAR(500) DEFAULT '/static/images/products/default-product.jpg';
ALTER TABLE product ADD COLUMN image_alt VARCHAR(200);

-- Добавляем поле для картинок категорий
ALTER TABLE category ADD COLUMN image_url VARCHAR(500) DEFAULT '/static/images/categories/default-category.jpg';

-- Обновляем существующие товары с картинками
UPDATE product SET image_url = '/static/images/products/milk.jpg' WHERE id = 1;
UPDATE product SET image_url = '/static/images/products/yogurt.jpg' WHERE id = 2;
UPDATE product SET image_url = '/static/images/products/cheese.jpg' WHERE id = 3;
UPDATE product SET image_url = '/static/images/products/chicken.jpg' WHERE id = 4;
UPDATE product SET image_url = '/static/images/products/mince.jpg' WHERE id = 5;
UPDATE product SET image_url = '/static/images/products/buckwheat.jpg' WHERE id = 6;
UPDATE product SET image_url = '/static/images/products/water.jpg' WHERE id = 7;
UPDATE product SET image_url = '/static/images/products/juice.jpg' WHERE id = 8;
UPDATE product SET image_url = '/static/images/products/cola.jpg' WHERE id = 9;
UPDATE product SET image_url = '/static/images/products/chocolate.jpg' WHERE id = 10;
UPDATE product SET image_url = '/static/images/products/oreo.jpg' WHERE id = 11;
UPDATE product SET image_url = '/static/images/products/dumplings.jpg' WHERE id = 12;
UPDATE product SET image_url = '/static/images/products/bread.jpg' WHERE id = 13;
UPDATE product SET image_url = '/static/images/products/bananas.jpg' WHERE id = 14;
UPDATE product SET image_url = '/static/images/products/apples.jpg' WHERE id = 15;

-- Обновляем картинки для категорий
UPDATE category SET image_url = '/static/images/categories/grocery.jpg' WHERE id = 1;
UPDATE category SET image_url = '/static/images/categories/dairy.jpg' WHERE id = 2;
UPDATE category SET image_url = '/static/images/categories/meat.jpg' WHERE id = 3;
UPDATE category SET image_url = '/static/images/categories/vegetables-fruits.jpg' WHERE id = 4;
UPDATE category SET image_url = '/static/images/categories/beverages.jpg' WHERE id = 5;
UPDATE category SET image_url = '/static/images/categories/confectionery.jpg' WHERE id = 6;
UPDATE category SET image_url = '/static/images/categories/bread.jpg' WHERE id = 7;
UPDATE category SET image_url = '/static/images/categories/ready-meals.jpg' WHERE id = 8;


USE product_store;

ALTER TABLE product ADD COLUMN IF NOT EXISTS image_url VARCHAR(500) DEFAULT '/static/images/products/default-product.jpg';
ALTER TABLE product ADD COLUMN IF NOT EXISTS image_alt VARCHAR(200);

ALTER TABLE category ADD COLUMN IF NOT EXISTS image_url VARCHAR(500) DEFAULT '/static/images/categories/default-category.jpg';

-- Обновляем картинки для существующих товаров
UPDATE product SET image_url = '/static/images/products/milk.jpg' WHERE name LIKE '%Молоко%';
UPDATE product SET image_url = '/static/images/products/yogurt.jpg' WHERE name LIKE '%Йогурт%';
UPDATE product SET image_url = '/static/images/products/cheese.jpg' WHERE name LIKE '%Сыр%';
UPDATE product SET image_url = '/static/images/products/chicken.jpg' WHERE name LIKE '%Куриное%';
UPDATE product SET image_url = '/static/images/products/mince.jpg' WHERE name LIKE '%Фарш%';
UPDATE product SET image_url = '/static/images/products/buckwheat.jpg' WHERE name LIKE '%Гречневая%';
UPDATE product SET image_url = '/static/images/products/water.jpg' WHERE name LIKE '%Вода%';
UPDATE product SET image_url = '/static/images/products/juice.jpg' WHERE name LIKE '%Сок%';
UPDATE product SET image_url = '/static/images/products/cola.jpg' WHERE name LIKE '%Coca%';
UPDATE product SET image_url = '/static/images/products/chocolate.jpg' WHERE name LIKE '%Шоколад%';
UPDATE product SET image_url = '/static/images/products/oreo.jpg' WHERE name LIKE '%Oreo%';
UPDATE product SET image_url = '/static/images/products/dumplings.jpg' WHERE name LIKE '%Пельмени%';
UPDATE product SET image_url = '/static/images/products/bread.jpg' WHERE name LIKE '%Хлеб%';
UPDATE product SET image_url = '/static/images/products/bananas.jpg' WHERE name LIKE '%Бананы%';
UPDATE product SET image_url = '/static/images/products/apples.jpg' WHERE name LIKE '%Яблоки%';

USE product_store;

-- Отключаем безопасный режим для текущей сессии
SET SQL_SAFE_UPDATES = 0;

-- Обновляем картинки категорий
UPDATE category SET image_url = '/static/images/categories/grocery.jpg' WHERE id = 1;
UPDATE category SET image_url = '/static/images/categories/dairy.jpg' WHERE id = 2;
UPDATE category SET image_url = '/static/images/categories/meat.jpg' WHERE id = 3;
UPDATE category SET image_url = '/static/images/categories/vegetables-fruits.jpg' WHERE id = 4;
UPDATE category SET image_url = '/static/images/categories/beverages.jpg' WHERE id = 5;
UPDATE category SET image_url = '/static/images/categories/confectionery.jpg' WHERE id = 6;
UPDATE category SET image_url = '/static/images/categories/bread.jpg' WHERE id = 7;
UPDATE category SET image_url = '/static/images/categories/ready-meals.jpg' WHERE id = 8;
UPDATE category SET image_url = '/static/images/categories/cereals.jpg' WHERE id = 9;
UPDATE category SET image_url = '/static/images/categories/pasta.jpg' WHERE id = 10;
UPDATE category SET image_url = '/static/images/categories/milk.jpg' WHERE id = 11;
UPDATE category SET image_url = '/static/images/categories/cheese.jpg' WHERE id = 12;
UPDATE category SET image_url = '/static/images/categories/yogurt.jpg' WHERE id = 13;
UPDATE category SET image_url = '/static/images/categories/beef.jpg' WHERE id = 14;
UPDATE category SET image_url = '/static/images/categories/chicken.jpg' WHERE id = 15;
UPDATE category SET image_url = '/static/images/categories/mince.jpg' WHERE id = 16;
UPDATE category SET image_url = '/static/images/categories/water.jpg' WHERE id = 17;
UPDATE category SET image_url = '/static/images/categories/juice.jpg' WHERE id = 18;
UPDATE category SET image_url = '/static/images/categories/soda.jpg' WHERE id = 19;
UPDATE category SET image_url = '/static/images/categories/chocolate.jpg' WHERE id = 20;
UPDATE category SET image_url = '/static/images/categories/cookies.jpg' WHERE id = 21;
UPDATE category SET image_url = '/static/images/categories/dumplings.jpg' WHERE id = 22;
UPDATE category SET image_url = '/static/images/categories/pizza.jpg' WHERE id = 23;
UPDATE category SET image_url = '/static/images/categories/ready-food.jpg' WHERE id = 24;

-- Обновляем картинки товаров
UPDATE product SET image_url = '/static/images/products/milk.jpg' WHERE id = 1;
UPDATE product SET image_url = '/static/images/products/yogurt.jpg' WHERE id = 2;
UPDATE product SET image_url = '/static/images/products/cheese.jpg' WHERE id = 3;
UPDATE product SET image_url = '/static/images/products/chicken.jpg' WHERE id = 4;
UPDATE product SET image_url = '/static/images/products/mince.jpg' WHERE id = 5;
UPDATE product SET image_url = '/static/images/products/buckwheat.jpg' WHERE id = 6;
UPDATE product SET image_url = '/static/images/products/water.jpg' WHERE id = 7;
UPDATE product SET image_url = '/static/images/products/juice.jpg' WHERE id = 8;
UPDATE product SET image_url = '/static/images/products/cola.jpg' WHERE id = 9;
UPDATE product SET image_url = '/static/images/products/chocolate.jpg' WHERE id = 10;
UPDATE product SET image_url = '/static/images/products/oreo.jpg' WHERE id = 11;
UPDATE product SET image_url = '/static/images/products/dumplings.jpg' WHERE id = 12;
UPDATE product SET image_url = '/static/images/products/bread.jpg' WHERE id = 13;
UPDATE product SET image_url = '/static/images/products/bananas.jpg' WHERE id = 14;
UPDATE product SET image_url = '/static/images/products/apples.jpg' WHERE id = 15;

-- Снова включаем безопасный режим (опционально)
SET SQL_SAFE_UPDATES = 1;

SELECT 'Готово! Картинки обновлены.' AS message;