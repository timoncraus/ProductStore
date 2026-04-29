DROP DATABASE IF EXISTS product_store;
CREATE DATABASE product_store;
USE product_store;

-- =====================================================
-- 1. ПОЛЬЗОВАТЕЛИ (раздельные имя и фамилия)
-- =====================================================
CREATE TABLE user (
    id INT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(50) UNIQUE NOT NULL,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    phone VARCHAR(20) NOT NULL,
    role ENUM('admin', 'user') DEFAULT 'user',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP NULL,
    is_active BOOLEAN DEFAULT TRUE
);

-- =====================================================
-- 2. СТРАНЫ (ДЛЯ АДРЕСОВ)
-- =====================================================
CREATE TABLE country (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) UNIQUE NOT NULL,
    code VARCHAR(10)
);

-- =====================================================
-- 3. РЕГИОНЫ/ОБЛАСТИ
-- =====================================================
CREATE TABLE region (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL,
    country_id INT NOT NULL,
    FOREIGN KEY (country_id) REFERENCES country(id) ON DELETE CASCADE
);

-- =====================================================
-- 4. НАСЕЛЕННЫЕ ПУНКТЫ (ГОРОДА, ПОСЕЛКИ, СЕЛА)
-- =====================================================
CREATE TABLE city (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL,
    region_id INT NOT NULL,
    FOREIGN KEY (region_id) REFERENCES region(id) ON DELETE CASCADE
);

-- =====================================================
-- 5. УЛИЦЫ
-- =====================================================
CREATE TABLE street (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL,
    city_id INT NOT NULL,
    FOREIGN KEY (city_id) REFERENCES city(id) ON DELETE CASCADE
);

-- =====================================================
-- 6. АДРЕСА ПОЛЬЗОВАТЕЛЕЙ
-- =====================================================
CREATE TABLE address (
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

-- =====================================================
-- 7. КАТЕГОРИИ ТОВАРОВ
-- =====================================================
CREATE TABLE category (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL,
    image_url VARCHAR(500) DEFAULT '/static/images/categories/default-category.jpg',
    sort_order INT DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE
);

-- =====================================================
-- 8. ЕДИНИЦЫ ИЗМЕРЕНИЯ (НОВАЯ ТАБЛИЦА)
-- =====================================================
CREATE TABLE unit (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(50) NOT NULL UNIQUE,
    short_name VARCHAR(20) NOT NULL,
    sort_order INT DEFAULT 0
);

-- =====================================================
-- 9. ТОВАРЫ (без unit, теперь unit_id)
-- =====================================================
CREATE TABLE product (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(200) NOT NULL,
    description TEXT,
    price DECIMAL(10,2) NOT NULL,
    old_price DECIMAL(10,2),
    image_url VARCHAR(500) DEFAULT '/static/images/products/default-product.jpg',
    image_alt VARCHAR(200),
    category_id INT NOT NULL,
    unit_id INT NOT NULL,
    stock INT DEFAULT 0,
    sales_count INT DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    is_new BOOLEAN DEFAULT FALSE,
    is_hit BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (category_id) REFERENCES category(id),
    FOREIGN KEY (unit_id) REFERENCES unit(id)
);

-- =====================================================
-- 10. СТАТУСЫ ЗАКАЗОВ
-- =====================================================
CREATE TABLE order_status (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(50) UNIQUE NOT NULL
);

-- =====================================================
-- 11. ЗАКАЗЫ (без recipient_name, recipient_phone, используется address_id)
-- =====================================================
CREATE TABLE orders (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    order_number VARCHAR(50) UNIQUE NOT NULL,
    total_amount DECIMAL(10,2) NOT NULL,
    address_id INT NOT NULL,
    comment TEXT,
    status_id INT DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES user(id),
    FOREIGN KEY (address_id) REFERENCES address(id),
    FOREIGN KEY (status_id) REFERENCES order_status(id)
);

-- =====================================================
-- 12. ТОВАРЫ В ЗАКАЗЕ
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
-- 13. КОРЗИНА
-- =====================================================
CREATE TABLE cart (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES user(id) ON DELETE CASCADE
);

-- =====================================================
-- 14. ТОВАРЫ В КОРЗИНЕ
-- =====================================================
CREATE TABLE cart_item (
    id INT PRIMARY KEY AUTO_INCREMENT,
    cart_id INT NOT NULL,
    product_id INT NOT NULL,
    quantity INT NOT NULL DEFAULT 1,
    price DECIMAL(10,2) NOT NULL DEFAULT 0,
    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (cart_id) REFERENCES cart(id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES product(id),
    UNIQUE KEY unique_cart_product (cart_id, product_id)
);

-- =====================================================
-- ИНДЕКСЫ ДЛЯ ОПТИМИЗАЦИИ
-- =====================================================
CREATE INDEX idx_product_category ON product(category_id);
CREATE INDEX idx_product_unit ON product(unit_id);
CREATE INDEX idx_product_price ON product(price);
CREATE INDEX idx_order_user ON orders(user_id);
CREATE INDEX idx_order_status ON orders(status_id);
CREATE INDEX idx_cart_user ON cart(user_id);
CREATE INDEX idx_address_user ON address(user_id);
CREATE INDEX idx_street_city ON street(city_id);
CREATE INDEX idx_city_region ON city(region_id);
CREATE INDEX idx_region_country ON region(country_id);

SELECT '=== СТРУКТУРА БАЗЫ ДАННЫХ СОЗДАНА УСПЕШНО ===' AS message;