-- =====================================================
-- ОЧИСТКА ВСЕХ ТАБЛИЦ (с учетом внешних ключей)
-- =====================================================

USE product_store;

SET FOREIGN_KEY_CHECKS = 0;
SET SQL_SAFE_UPDATES = 0;

-- Очистка таблиц с данными (в правильном порядке)
TRUNCATE TABLE order_item;
TRUNCATE TABLE orders;
TRUNCATE TABLE cart_item;
TRUNCATE TABLE cart;
TRUNCATE TABLE address;
TRUNCATE TABLE street;
TRUNCATE TABLE city;
TRUNCATE TABLE region;
TRUNCATE TABLE country;
TRUNCATE TABLE user;
TRUNCATE TABLE product;
TRUNCATE TABLE category;
TRUNCATE TABLE order_status;

-- Сброс AUTO_INCREMENT (опционально)
ALTER TABLE user AUTO_INCREMENT = 1;
ALTER TABLE country AUTO_INCREMENT = 1;
ALTER TABLE region AUTO_INCREMENT = 1;
ALTER TABLE city AUTO_INCREMENT = 1;
ALTER TABLE street AUTO_INCREMENT = 1;
ALTER TABLE address AUTO_INCREMENT = 1;
ALTER TABLE product AUTO_INCREMENT = 1;
ALTER TABLE category AUTO_INCREMENT = 1;
ALTER TABLE orders AUTO_INCREMENT = 1;
ALTER TABLE order_item AUTO_INCREMENT = 1;
ALTER TABLE cart AUTO_INCREMENT = 1;
ALTER TABLE cart_item AUTO_INCREMENT = 1;

SET FOREIGN_KEY_CHECKS = 1;
SET SQL_SAFE_UPDATES = 1;

SELECT 'ВСЕ ТАБЛИЦЫ ОЧИЩЕНЫ!' AS message;

-- =====================================================
-- НАПОЛНЕНИЕ БАЗЫ ДАННЫХ product_store
-- =====================================================

USE product_store;

SET FOREIGN_KEY_CHECKS = 0;
SET SQL_SAFE_UPDATES = 0;

-- =====================================================
-- 1. ПОЛЬЗОВАТЕЛИ (пароль: Admin123! - хэш)
-- =====================================================
INSERT INTO user (username, first_name, last_name, email, phone, password_hash, role) VALUES
('admin', 'Администратор', '', 'admin@example.com', '+79990000000', '8d969eef6ecad3c29a3a629280e686cf0c3f5d5a86aff3ca12020c923adc6c92', 'admin'),
('ivan', 'Иван', 'Петров', 'ivan@mail.ru', '+79123456789', '8d969eef6ecad3c29a3a629280e686cf0c3f5d5a86aff3ca12020c923adc6c92', 'user'),
('maria', 'Мария', 'Сидорова', 'maria@mail.ru', '+79234567890', '8d969eef6ecad3c29a3a629280e686cf0c3f5d5a86aff3ca12020c923adc6c92', 'user'),
('alexey', 'Алексей', 'Кузнецов', 'alexey@mail.ru', '+79345678901', '8d969eef6ecad3c29a3a629280e686cf0c3f5d5a86aff3ca12020c923adc6c92', 'user'),
('elena', 'Елена', 'Михайлова', 'elena@mail.ru', '+79456789012', '8d969eef6ecad3c29a3a629280e686cf0c3f5d5a86aff3ca12020c923adc6c92', 'user');

-- =====================================================
-- 2. СТРАНЫ
-- =====================================================
INSERT INTO country (name, code) VALUES 
('Россия', 'RU'), 
('Беларусь', 'BY'), 
('Казахстан', 'KZ'),
('Украина', 'UA'),
('Армения', 'AM'),
('Грузия', 'GE'),
('Узбекистан', 'UZ');

-- =====================================================
-- 3. РЕГИОНЫ РОССИИ
-- =====================================================
INSERT INTO region (name, country_id) VALUES 
('Москва', 1),
('Московская область', 1),
('Санкт-Петербург', 1),
('Ленинградская область', 1),
('Новосибирская область', 1),
('Свердловская область', 1),
('Татарстан', 1),
('Краснодарский край', 1),
('Ростовская область', 1),
('Нижегородская область', 1),
('Самарская область', 1),
('Челябинская область', 1),
('Красноярский край', 1),
('Пермский край', 1),
('Волгоградская область', 1),
('Оренбургская область', 1),
('Республика Башкортостан', 1),
('Тюменская область', 1),
('Иркутская область', 1),
('Воронежская область', 1);

-- =====================================================
-- 4. ГОРОДА
-- =====================================================
INSERT INTO city (name, region_id) VALUES 
-- Москва и область
('Москва', 1),
('Одинцово', 2),
('Красногорск', 2),
('Химки', 2),
('Подольск', 2),
('Люберцы', 2),
('Королев', 2),
('Балашиха', 2),
('Мытищи', 2),
-- Санкт-Петербург и область
('Санкт-Петербург', 3),
('Всеволожск', 4),
('Гатчина', 4),
('Выборг', 4),
('Пушкин', 4),
('Павловск', 4),
-- Новосибирская область
('Новосибирск', 5),
('Бердск', 5),
('Искитим', 5),
-- Свердловская область
('Екатеринбург', 6),
('Нижний Тагил', 6),
('Каменск-Уральский', 6),
-- Татарстан
('Казань', 7),
('Набережные Челны', 7),
('Елабуга', 7),
-- Краснодарский край
('Краснодар', 8),
('Сочи', 8),
('Новороссийск', 8),
('Анапа', 8),
('Геленджик', 8),
-- Ростовская область
('Ростов-на-Дону', 9),
('Таганрог', 9),
('Шахты', 9),
-- Нижегородская область
('Нижний Новгород', 10),
('Дзержинск', 10),
('Арзамас', 10),
-- Самарская область
('Самара', 11),
('Тольятти', 11),
('Сызрань', 11),
-- Челябинская область
('Челябинск', 12),
('Магнитогорск', 12),
-- Красноярский край
('Красноярск', 13),
-- Пермский край
('Пермь', 14),
-- Волгоградская область
('Волгоград', 15),
-- Оренбургская область
('Оренбург', 16),
('Орск', 16),
('Новотроицк', 16),
('Бузулук', 16),
('Соль-Илецк', 16),
('Гай', 16),
('Медногорск', 16),
('Кувандык', 16),
('Сорочинск', 16),
('Абдулино', 16),
('Ясный', 16),
-- Республика Башкортостан
('Уфа', 17),
('Стерлитамак', 17),
('Салават', 17),
-- Тюменская область
('Тюмень', 18),
-- Иркутская область
('Иркутск', 19),
-- Воронежская область
('Воронеж', 20);

-- =====================================================
-- 5. УЛИЦЫ (с использованием подзапросов для правильных city_id)
-- =====================================================

-- МОСКВА
INSERT INTO street (name, city_id) 
SELECT name, (SELECT id FROM city WHERE name = 'Москва' LIMIT 1) FROM (
    SELECT 'Тверская' as name UNION ALL
    SELECT 'Арбат' UNION ALL
    SELECT 'Новый Арбат' UNION ALL
    SELECT 'Ленинский проспект' UNION ALL
    SELECT 'Кутузовский проспект' UNION ALL
    SELECT 'Проспект Мира' UNION ALL
    SELECT 'Ленинградский проспект' UNION ALL
    SELECT 'Садовое кольцо' UNION ALL
    SELECT 'Бульварное кольцо' UNION ALL
    SELECT 'Покровка' UNION ALL
    SELECT 'Мясницкая' UNION ALL
    SELECT 'Большая Дмитровка' UNION ALL
    SELECT 'Петровка' UNION ALL
    SELECT 'Цветной бульвар' UNION ALL
    SELECT 'Рождественский бульвар' UNION ALL
    SELECT 'Страстной бульвар' UNION ALL
    SELECT 'Чистопрудный бульвар' UNION ALL
    SELECT 'Пресненская набережная' UNION ALL
    SELECT 'Льва Толстого' UNION ALL
    SELECT 'Остоженка' UNION ALL
    SELECT 'Пречистенка'
) AS streets;

-- САНКТ-ПЕТЕРБУРГ
INSERT INTO street (name, city_id) 
SELECT name, (SELECT id FROM city WHERE name = 'Санкт-Петербург' LIMIT 1) FROM (
    SELECT 'Невский проспект' as name UNION ALL
    SELECT 'Московский проспект' UNION ALL
    SELECT 'Лиговский проспект' UNION ALL
    SELECT 'Большой проспект П.С.' UNION ALL
    SELECT 'Садовая улица' UNION ALL
    SELECT 'Набережная реки Фонтанки' UNION ALL
    SELECT 'Каменноостровский проспект' UNION ALL
    SELECT 'Владимирский проспект' UNION ALL
    SELECT 'Загородный проспект' UNION ALL
    SELECT 'Рубинштейна' UNION ALL
    SELECT 'Малая Садовая' UNION ALL
    SELECT 'Большая Конюшенная' UNION ALL
    SELECT 'Некрасова' UNION ALL
    SELECT 'Восстания' UNION ALL
    SELECT 'Ломоносова'
) AS streets;

-- ЕКАТЕРИНБУРГ
INSERT INTO street (name, city_id) 
SELECT name, (SELECT id FROM city WHERE name = 'Екатеринбург' LIMIT 1) FROM (
    SELECT 'Ленина' as name UNION ALL
    SELECT 'Малышева' UNION ALL
    SELECT 'Татищева' UNION ALL
    SELECT 'Белинского' UNION ALL
    SELECT 'Московская' UNION ALL
    SELECT 'Луначарского' UNION ALL
    SELECT 'Щорса' UNION ALL
    SELECT 'Куйбышева' UNION ALL
    SELECT 'Свердлова' UNION ALL
    SELECT 'Карла Либкнехта' UNION ALL
    SELECT 'Тверитина' UNION ALL
    SELECT '8 Марта' UNION ALL
    SELECT 'Фрунзе'
) AS streets;

-- КАЗАНЬ
INSERT INTO street (name, city_id) 
SELECT name, (SELECT id FROM city WHERE name = 'Казань' LIMIT 1) FROM (
    SELECT 'Баумана' as name UNION ALL
    SELECT 'Кремлевская' UNION ALL
    SELECT 'Петербургская' UNION ALL
    SELECT 'Карла Маркса' UNION ALL
    SELECT 'Пушкина' UNION ALL
    SELECT 'Гоголя' UNION ALL
    SELECT 'Толстого' UNION ALL
    SELECT 'Чернышевского' UNION ALL
    SELECT 'Университетская' UNION ALL
    SELECT 'Дзержинского' UNION ALL
    SELECT 'Татарстан' UNION ALL
    SELECT 'Чистопольская'
) AS streets;

-- НОВОСИБИРСК
INSERT INTO street (name, city_id) 
SELECT name, (SELECT id FROM city WHERE name = 'Новосибирск' LIMIT 1) FROM (
    SELECT 'Красный проспект' as name UNION ALL
    SELECT 'Ленина' UNION ALL
    SELECT 'Димитрова' UNION ALL
    SELECT 'Горького' UNION ALL
    SELECT 'Кирова' UNION ALL
    SELECT 'Советская' UNION ALL
    SELECT 'Вокзальная магистраль' UNION ALL
    SELECT 'Писарева' UNION ALL
    SELECT 'Серебренниковская' UNION ALL
    SELECT 'Фрунзе'
) AS streets;

-- КРАСНОДАР
INSERT INTO street (name, city_id) 
SELECT name, (SELECT id FROM city WHERE name = 'Краснодар' LIMIT 1) FROM (
    SELECT 'Красная' as name UNION ALL
    SELECT 'Северная' UNION ALL
    SELECT 'Ставропольская' UNION ALL
    SELECT 'Калинина' UNION ALL
    SELECT 'Кубанская набережная' UNION ALL
    SELECT 'Рашпилевская' UNION ALL
    SELECT 'Коммунаров' UNION ALL
    SELECT 'Октябрьская'
) AS streets;

-- СОЧИ
INSERT INTO street (name, city_id) 
SELECT name, (SELECT id FROM city WHERE name = 'Сочи' LIMIT 1) FROM (
    SELECT 'Навагинская' as name UNION ALL
    SELECT 'Курортный проспект' UNION ALL
    SELECT 'Московская' UNION ALL
    SELECT 'Виноградная' UNION ALL
    SELECT 'Пластунская' UNION ALL
    SELECT 'Донская'
) AS streets;

-- РОСТОВ-НА-ДОНУ
INSERT INTO street (name, city_id) 
SELECT name, (SELECT id FROM city WHERE name = 'Ростов-на-Дону' LIMIT 1) FROM (
    SELECT 'Большая Садовая' as name UNION ALL
    SELECT 'Пушкинская' UNION ALL
    SELECT 'Кировский проспект' UNION ALL
    SELECT 'Буденновский проспект' UNION ALL
    SELECT 'Ворошиловский проспект' UNION ALL
    SELECT 'Театральный проспект' UNION ALL
    SELECT 'Набережная'
) AS streets;

-- ОРЕНБУРГ (50+ улиц)
INSERT INTO street (name, city_id) 
SELECT name, (SELECT id FROM city WHERE name = 'Оренбург' LIMIT 1) FROM (
    SELECT 'Советская' as name UNION ALL
    SELECT 'Ленинская' UNION ALL
    SELECT 'Постникова' UNION ALL
    SELECT 'Чкалова' UNION ALL
    SELECT 'Терешковой' UNION ALL
    SELECT 'Мира' UNION ALL
    SELECT 'Гагарина' UNION ALL
    SELECT 'Пушкинская' UNION ALL
    SELECT 'Володарского' UNION ALL
    SELECT 'Кирова' UNION ALL
    SELECT 'Степана Разина' UNION ALL
    SELECT 'Парковый проспект' UNION ALL
    SELECT 'Донгузская' UNION ALL
    SELECT 'Шевченко' UNION ALL
    SELECT 'Карагандинская' UNION ALL
    SELECT 'Бурзянцева' UNION ALL
    SELECT 'Рыбаковская' UNION ALL
    SELECT 'Новая' UNION ALL
    SELECT 'Ткачева' UNION ALL
    SELECT 'Дзержинского' UNION ALL
    SELECT 'Ромашковская' UNION ALL
    SELECT 'Загородное шоссе' UNION ALL
    SELECT 'Малая Земля' UNION ALL
    SELECT 'Транспортная' UNION ALL
    SELECT 'Салмышская' UNION ALL
    SELECT 'Орская' UNION ALL
    SELECT 'Цвиллинга' UNION ALL
    SELECT 'Стрелковая' UNION ALL
    SELECT 'Монтажников' UNION ALL
    SELECT 'Серова' UNION ALL
    SELECT 'Комсомольская' UNION ALL
    SELECT 'Октябрьская' UNION ALL
    SELECT 'Революционная' UNION ALL
    SELECT 'Пионерская' UNION ALL
    SELECT 'Луговая' UNION ALL
    SELECT 'Степная' UNION ALL
    SELECT 'Уральская' UNION ALL
    SELECT 'Железнодорожная' UNION ALL
    SELECT 'Вокзальная' UNION ALL
    SELECT 'Индустриальная' UNION ALL
    SELECT 'Заводская' UNION ALL
    SELECT 'Южная' UNION ALL
    SELECT 'Северная' UNION ALL
    SELECT 'Восточная' UNION ALL
    SELECT 'Западная' UNION ALL
    SELECT 'Центральная' UNION ALL
    SELECT 'Молодежная' UNION ALL
    SELECT 'Строителей' UNION ALL
    SELECT 'Нефтяников' UNION ALL
    SELECT 'Машиностроителей' UNION ALL
    SELECT 'Энергетиков'
) AS streets;

-- ОРСК
INSERT INTO street (name, city_id) 
SELECT name, (SELECT id FROM city WHERE name = 'Орск' LIMIT 1) FROM (
    SELECT 'Ленина' as name UNION ALL
    SELECT 'Мира' UNION ALL
    SELECT 'Станиславского' UNION ALL
    SELECT 'Краматорская' UNION ALL
    SELECT 'Нефтяников' UNION ALL
    SELECT 'Шелухина' UNION ALL
    SELECT 'Московская' UNION ALL
    SELECT 'Новая' UNION ALL
    SELECT 'Советская' UNION ALL
    SELECT 'Орджоникидзе'
) AS streets;

-- НОВОТРОИЦК
INSERT INTO street (name, city_id) 
SELECT name, (SELECT id FROM city WHERE name = 'Новотроицк' LIMIT 1) FROM (
    SELECT 'Советская' as name UNION ALL
    SELECT 'Металлургов' UNION ALL
    SELECT 'Железнодорожная' UNION ALL
    SELECT 'Комсомольская' UNION ALL
    SELECT 'Уральская' UNION ALL
    SELECT 'Победы' UNION ALL
    SELECT 'Ленина' UNION ALL
    SELECT 'Гагарина'
) AS streets;

-- БУЗУЛУК
INSERT INTO street (name, city_id) 
SELECT name, (SELECT id FROM city WHERE name = 'Бузулук' LIMIT 1) FROM (
    SELECT 'Ленина' as name UNION ALL
    SELECT 'Московская' UNION ALL
    SELECT 'Чапаева' UNION ALL
    SELECT 'Кирова' UNION ALL
    SELECT 'Октябрьская' UNION ALL
    SELECT '1 Мая' UNION ALL
    SELECT 'Советская' UNION ALL
    SELECT 'Гагарина'
) AS streets;

-- СОЛЬ-ИЛЕЦК
INSERT INTO street (name, city_id) 
SELECT name, (SELECT id FROM city WHERE name = 'Соль-Илецк' LIMIT 1) FROM (
    SELECT 'Ленина' as name UNION ALL
    SELECT 'Оренбургская' UNION ALL
    SELECT 'Степная' UNION ALL
    SELECT 'Уральская' UNION ALL
    SELECT 'Курортная' UNION ALL
    SELECT 'Советская'
) AS streets;

-- УФА
INSERT INTO street (name, city_id) 
SELECT name, (SELECT id FROM city WHERE name = 'Уфа' LIMIT 1) FROM (
    SELECT 'Ленина' as name UNION ALL
    SELECT 'Кирова' UNION ALL
    SELECT 'Октября проспект' UNION ALL
    SELECT 'Цюрупы' UNION ALL
    SELECT 'Коммунистическая' UNION ALL
    SELECT 'Пушкина' UNION ALL
    SELECT 'Карла Маркса' UNION ALL
    SELECT 'Заки Валиди' UNION ALL
    SELECT 'Гоголя'
) AS streets;

-- ЧЕЛЯБИНСК
INSERT INTO street (name, city_id) 
SELECT name, (SELECT id FROM city WHERE name = 'Челябинск' LIMIT 1) FROM (
    SELECT 'Ленина' as name UNION ALL
    SELECT 'Кирова' UNION ALL
    SELECT 'Труда' UNION ALL
    SELECT 'Воровского' UNION ALL
    SELECT 'Коммуны' UNION ALL
    SELECT 'Свердловский проспект'
) AS streets;

-- САМАРА
INSERT INTO street (name, city_id) 
SELECT name, (SELECT id FROM city WHERE name = 'Самара' LIMIT 1) FROM (
    SELECT 'Ленина' as name UNION ALL
    SELECT 'Куйбышева' UNION ALL
    SELECT 'Московское шоссе' UNION ALL
    SELECT 'Полевая' UNION ALL
    SELECT 'Садовая' UNION ALL
    SELECT 'Победы'
) AS streets;

-- НИЖНИЙ НОВГОРОД
INSERT INTO street (name, city_id) 
SELECT name, (SELECT id FROM city WHERE name = 'Нижний Новгород' LIMIT 1) FROM (
    SELECT 'Большая Покровская' as name UNION ALL
    SELECT 'Максима Горького' UNION ALL
    SELECT 'Белинского' UNION ALL
    SELECT 'Рождественская' UNION ALL
    SELECT 'Варварская'
) AS streets;

-- ВОРОНЕЖ
INSERT INTO street (name, city_id) 
SELECT name, (SELECT id FROM city WHERE name = 'Воронеж' LIMIT 1) FROM (
    SELECT 'Ленина' as name UNION ALL
    SELECT 'Плехановская' UNION ALL
    SELECT 'Кирова' UNION ALL
    SELECT 'Фридриха Энгельса' UNION ALL
    SELECT 'Революции проспект'
) AS streets;

-- ПЕРМЬ
INSERT INTO street (name, city_id) 
SELECT name, (SELECT id FROM city WHERE name = 'Пермь' LIMIT 1) FROM (
    SELECT 'Ленина' as name UNION ALL
    SELECT 'Комсомольский проспект' UNION ALL
    SELECT 'Петропавловская' UNION ALL
    SELECT 'Мира'
) AS streets;

-- КРАСНОЯРСК
INSERT INTO street (name, city_id) 
SELECT name, (SELECT id FROM city WHERE name = 'Красноярск' LIMIT 1) FROM (
    SELECT 'Мира проспект' as name UNION ALL
    SELECT 'Ленина' UNION ALL
    SELECT 'Красноярский рабочий' UNION ALL
    SELECT 'Карла Маркса'
) AS streets;

-- ТЮМЕНЬ
INSERT INTO street (name, city_id) 
SELECT name, (SELECT id FROM city WHERE name = 'Тюмень' LIMIT 1) FROM (
    SELECT 'Республики' as name UNION ALL
    SELECT 'Ленина' UNION ALL
    SELECT 'Мельникайте' UNION ALL
    SELECT 'Пермякова'
) AS streets;

-- ВОЛГОГРАД
INSERT INTO street (name, city_id) 
SELECT name, (SELECT id FROM city WHERE name = 'Волгоград' LIMIT 1) FROM (
    SELECT 'Ленина проспект' as name UNION ALL
    SELECT 'Мира' UNION ALL
    SELECT 'Комсомольская' UNION ALL
    SELECT 'Калинина'
) AS streets;

-- =====================================================
-- 6. АДРЕСА ПОЛЬЗОВАТЕЛЕЙ
-- =====================================================
INSERT INTO address (user_id, street_id, house, apartment, entrance, floor, postal_code, is_default) VALUES
(2, (SELECT id FROM street WHERE name = 'Тверская' AND city_id = (SELECT id FROM city WHERE name = 'Москва') LIMIT 1), '15', '78', '3', 7, '125009', TRUE),
(2, (SELECT id FROM street WHERE name = 'Мясницкая' AND city_id = (SELECT id FROM city WHERE name = 'Москва') LIMIT 1), '25', '12', '2', 4, '107031', FALSE),
(3, (SELECT id FROM street WHERE name = 'Невский проспект' AND city_id = (SELECT id FROM city WHERE name = 'Санкт-Петербург') LIMIT 1), '10', '45', '1', 5, '191186', TRUE),
(4, (SELECT id FROM street WHERE name = 'Баумана' AND city_id = (SELECT id FROM city WHERE name = 'Казань') LIMIT 1), '22', '8', '2', 3, '420111', TRUE),
(5, (SELECT id FROM street WHERE name = 'Ленина' AND city_id = (SELECT id FROM city WHERE name = 'Екатеринбург') LIMIT 1), '8', '34', '1', 6, '620014', TRUE),
(2, (SELECT id FROM street WHERE name = 'Советская' AND city_id = (SELECT id FROM city WHERE name = 'Оренбург') LIMIT 1), '50', '120', '1', 4, '460000', FALSE),
(3, (SELECT id FROM street WHERE name = 'Постникова' AND city_id = (SELECT id FROM city WHERE name = 'Оренбург') LIMIT 1), '25', '5', '2', 3, '460000', FALSE);

-- =====================================================
-- 7. СТАТУСЫ ЗАКАЗОВ
-- =====================================================
INSERT INTO order_status (name) VALUES 
('Новый'), 
('Подтвержден'), 
('Оплачен'), 
('Отправлен'), 
('Доставлен'), 
('Отменен');

-- =====================================================
-- 8. КАТЕГОРИИ ТОВАРОВ
-- =====================================================
INSERT INTO category (id, name, image_url, sort_order) VALUES
(1, 'Бакалея', '/static/images/categories/grocery.jpg', 1),
(2, 'Молочные продукты', '/static/images/categories/dairy.jpg', 2),
(3, 'Мясо и птица', '/static/images/categories/meat.jpg', 3),
(4, 'Овощи и фрукты', '/static/images/categories/vegetables-fruits.jpg', 4),
(5, 'Напитки', '/static/images/categories/beverages.jpg', 5),
(6, 'Кондитерские изделия', '/static/images/categories/confectionery.jpg', 6),
(7, 'Хлеб и выпечка', '/static/images/categories/bread.jpg', 7),
(8, 'Полуфабрикаты', '/static/images/categories/ready-meals.jpg', 8);

-- =====================================================
-- 9. ТОВАРЫ
-- =====================================================
INSERT INTO product (id, name, description, price, old_price, image_url, category_id, stock, unit, sales_count, is_new, is_hit) VALUES
-- Бакалея (1-10)
(1, 'Гречневая крупа "Мистраль"', 'Ядрица высшего сорта. Быстро варится, рассыпчатая.', 89.90, 109.90, '/static/images/products/buckwheat.jpg', 1, 500, 'кг', 1800, FALSE, TRUE),
(2, 'Рис "Басмати"', 'Длиннозерный рис с ароматом. Идеален для плова.', 159.90, 189.90, '/static/images/products/rice.jpg', 1, 300, 'кг', 980, FALSE, TRUE),
(3, 'Овсяные хлопья "Геркулес"', 'Классические овсяные хлопья для здорового завтрака.', 79.90, 99.90, '/static/images/products/oatmeal.jpg', 1, 400, 'кг', 2340, FALSE, FALSE),
(4, 'Макароны Barilla Спагетти', 'Спагетти из твердых сортов пшеницы.', 129.90, NULL, '/static/images/products/pasta.jpg', 1, 200, 'уп', 3450, FALSE, TRUE),
(5, 'Мука пшеничная в/с', 'Мука высшего сорта. 1 кг.', 59.90, NULL, '/static/images/products/flour.jpg', 1, 600, 'кг', 1200, FALSE, FALSE),
(6, 'Сахар песок', 'Сахар-песок рафинированный.', 69.90, 79.90, '/static/images/products/sugar.jpg', 1, 800, 'кг', 3400, FALSE, FALSE),
(7, 'Соль поваренная', 'Соль поваренная пищевая. 1 кг.', 29.90, NULL, '/static/images/products/salt.jpg', 1, 1000, 'кг', 2100, FALSE, FALSE),
(8, 'Масло подсолнечное', 'Рафинированное дезодорированное масло. 1 л.', 119.90, 139.90, '/static/images/products/oil.jpg', 1, 300, 'л', 890, FALSE, FALSE),
(9, 'Пшено шлифованное', 'Для рассыпчатых каш.', 59.90, NULL, '/static/images/products/millet.jpg', 1, 250, 'кг', 560, FALSE, FALSE),
(10, 'Киноа', 'Суперфуд. Без глютена.', 399.90, 499.90, '/static/images/products/quinoa.jpg', 1, 100, 'кг', 340, TRUE, TRUE),

-- Молочные продукты (11-20)
(11, 'Молоко 3.2% "Домик в деревне"', 'Пастеризованное молоко. 1 л.', 89.90, 99.90, '/static/images/products/milk.jpg', 2, 500, 'л', 5200, FALSE, TRUE),
(12, 'Кефир 2.5%', 'Натуральный кефир. 1 л.', 79.90, NULL, '/static/images/products/kefir.jpg', 2, 400, 'л', 3100, FALSE, FALSE),
(13, 'Сметана 20%', 'Домашняя сметана. 400 г.', 129.90, 149.90, '/static/images/products/sour-cream.jpg', 2, 200, 'шт', 2300, FALSE, FALSE),
(14, 'Творог 9%', 'Рассыпчатый творог. 500 г.', 159.90, 179.90, '/static/images/products/cottage-cheese.jpg', 2, 150, 'шт', 1800, FALSE, TRUE),
(15, 'Сыр "Российский"', 'Твердый сыр 50%. 200 г.', 179.90, 199.90, '/static/images/products/cheese.jpg', 2, 200, 'шт', 890, FALSE, TRUE),
(16, 'Йогурт Activia натуральный', 'Натуральный йогурт. 125 г.', 75.00, 89.90, '/static/images/products/yogurt.jpg', 2, 1000, 'шт', 3100, TRUE, FALSE),
(17, 'Масло сливочное 82.5%', 'Крестьянское масло. 180 г.', 149.90, 169.90, '/static/images/products/butter.jpg', 2, 300, 'шт', 2100, FALSE, FALSE),
(18, 'Ряженка 4%', 'Топленое молоко сквашенное.', 89.90, NULL, '/static/images/products/ryazhenka.jpg', 2, 250, 'л', 1200, FALSE, FALSE),
(19, 'Сыр "Пармезан"', 'Твердый итальянский сыр.', 1899.00, 2199.00, '/static/images/products/parmesan.jpg', 2, 50, 'кг', 430, TRUE, TRUE),
(20, 'Моцарелла', 'Мягкий сыр для пиццы.', 399.00, NULL, '/static/images/products/mozzarella.jpg', 2, 150, 'шт', 2100, FALSE, FALSE),

-- Мясо и птица (21-25)
(21, 'Куриное филе охлажденное', 'Охлажденное куриное филе. 1 кг.', 349.90, 399.90, '/static/images/products/chicken.jpg', 3, 150, 'кг', 1450, FALSE, TRUE),
(22, 'Куриные крылья', 'Для гриля и запекания. 1 кг.', 249.90, NULL, '/static/images/products/wings.jpg', 3, 200, 'кг', 1230, FALSE, FALSE),
(23, 'Говядина вырезка', 'Нежная говяжья вырезка. 1 кг.', 899.00, 999.00, '/static/images/products/beef.jpg', 3, 80, 'кг', 560, FALSE, TRUE),
(24, 'Фарш говяжий', 'Натуральный фарш 80/20. 1 кг.', 399.90, 449.90, '/static/images/products/mince.jpg', 3, 120, 'кг', 1320, FALSE, FALSE),
(25, 'Фарш куриный', 'Нежный куриный фарш. 1 кг.', 299.90, NULL, '/static/images/products/chicken-mince.jpg', 3, 100, 'кг', 670, FALSE, FALSE),

-- Овощи и фрукты (26-32)
(26, 'Бананы', 'Спелые сладкие бананы. 1 кг.', 129.90, 149.90, '/static/images/products/bananas.jpg', 4, 300, 'кг', 5400, FALSE, TRUE),
(27, 'Яблоки "Голден"', 'Сочные сладкие яблоки. 1 кг.', 119.90, 139.90, '/static/images/products/apples.jpg', 4, 250, 'кг', 4900, FALSE, TRUE),
(28, 'Апельсины', 'Сочные апельсины. 1 кг.', 139.90, 159.90, '/static/images/products/oranges.jpg', 4, 200, 'кг', 3800, FALSE, FALSE),
(29, 'Картофель', 'Молодой картофель. 1 кг.', 59.90, 79.90, '/static/images/products/potatoes.jpg', 4, 800, 'кг', 8900, FALSE, FALSE),
(30, 'Помидоры', 'Спелые помидоры. 1 кг.', 199.90, 249.90, '/static/images/products/tomatoes.jpg', 4, 150, 'кг', 4500, FALSE, FALSE),
(31, 'Огурцы', 'Хрустящие огурцы. 1 кг.', 159.90, 199.90, '/static/images/products/cucumbers.jpg', 4, 180, 'кг', 4300, FALSE, FALSE),
(32, 'Лимоны', 'Свежие лимоны.', 89.90, NULL, '/static/images/products/lemons.jpg', 4, 200, 'кг', 2100, FALSE, FALSE),

-- Напитки (33-38)
(33, 'Вода "Святой источник" 1.5л', 'Питьевая вода первой категории.', 49.90, 59.90, '/static/images/products/water.jpg', 5, 2000, 'шт', 8600, FALSE, TRUE),
(34, 'Сок "Добрый" апельсиновый', 'Сок прямого отжима. 1 л.', 129.90, 149.90, '/static/images/products/juice.jpg', 5, 800, 'шт', 4800, FALSE, FALSE),
(35, 'Coca-Cola 0.5л', 'Классическая Coca-Cola.', 89.90, 99.90, '/static/images/products/cola.jpg', 5, 1500, 'шт', 12900, FALSE, TRUE),
(36, 'Квас "Очаковский" 1.5л', 'Натуральный квас брожения.', 129.90, 149.90, '/static/images/products/kvass.jpg', 5, 500, 'шт', 3400, FALSE, FALSE),
(37, 'Чай Lipton чёрный', 'Чай в пакетиках. 25 шт.', 159.90, 179.90, '/static/images/products/tea.jpg', 5, 300, 'уп', 2100, FALSE, FALSE),
(38, 'Кофе Jacobs молотый', 'Молотый кофе. 250 г.', 349.90, 399.90, '/static/images/products/coffee.jpg', 5, 200, 'шт', 1560, TRUE, TRUE),

-- Кондитерские изделия (39-44)
(39, 'Шоколад Milka молочный', 'Молочный шоколад. 90 г.', 129.90, 149.90, '/static/images/products/chocolate.jpg', 6, 600, 'шт', 6500, FALSE, TRUE),
(40, 'Печенье Oreo', 'Хрустящее печенье с кремом. 150 г.', 99.90, 119.90, '/static/images/products/oreo.jpg', 6, 800, 'шт', 8700, FALSE, TRUE),
(41, 'Конфеты "Коровка"', 'Молочные конфеты. 500 г.', 199.90, 249.90, '/static/images/products/candies.jpg', 6, 400, 'уп', 3400, FALSE, FALSE),
(42, 'Пряники тульские', 'Медовые пряники. 300 г.', 89.90, NULL, '/static/images/products/gingerbread.jpg', 6, 500, 'уп', 2300, FALSE, FALSE),
(43, 'Вафли "Артек"', 'Сливочные вафли. 200 г.', 79.90, 89.90, '/static/images/products/waffles.jpg', 6, 600, 'шт', 2100, FALSE, FALSE),
(44, 'Зефир ванильный', 'Нежный зефир. 300 г.', 119.90, 139.90, '/static/images/products/zephyr.jpg', 6, 350, 'уп', 1800, TRUE, FALSE),

-- Хлеб и выпечка (45-48)
(45, 'Хлеб "Бородинский"', 'Ржаной хлеб с тмином.', 59.90, 69.90, '/static/images/products/borodinsky.jpg', 7, 400, 'шт', 6500, FALSE, TRUE),
(46, 'Батон нарезной', 'Пшеничный батон.', 49.90, 59.90, '/static/images/products/white-bread.jpg', 7, 600, 'шт', 8900, FALSE, FALSE),
(47, 'Лаваш армянский', 'Тонкий лаваш. 300 г.', 39.90, 49.90, '/static/images/products/lavash.jpg', 7, 500, 'шт', 5600, FALSE, FALSE),
(48, 'Булочка с маком', 'Сдобная булочка.', 29.90, NULL, '/static/images/products/bun.jpg', 7, 700, 'шт', 6700, FALSE, FALSE),

-- Полуфабрикаты (49-52)
(49, 'Пельмени "Сибирские"', 'Домашние пельмени. 800 г.', 349.90, 399.90, '/static/images/products/dumplings.jpg', 8, 200, 'уп', 1340, FALSE, FALSE),
(50, 'Вареники с картошкой', 'Вареники с картофелем. 800 г.', 249.90, 299.90, '/static/images/products/varenyky.jpg', 8, 180, 'уп', 890, FALSE, FALSE),
(51, 'Пицца "Маргарита"', 'Замороженная пицца. 350 г.', 299.90, 349.90, '/static/images/products/pizza.jpg', 8, 150, 'шт', 1230, FALSE, FALSE),
(52, 'Котлеты куриные', 'Замороженные котлеты. 400 г.', 249.90, 299.90, '/static/images/products/cutlets.jpg', 8, 120, 'уп', 890, FALSE, FALSE);

-- =====================================================
-- 10. КОРЗИНЫ ДЛЯ ПОЛЬЗОВАТЕЛЕЙ
-- =====================================================
INSERT INTO cart (user_id) VALUES (2), (3), (4), (5);

-- =====================================================
-- 11. ТОВАРЫ В КОРЗИНАХ
-- =====================================================
INSERT INTO cart_item (cart_id, product_id, quantity, price) VALUES
(1, 1, 2, 89.90),
(1, 11, 1, 89.90),
(2, 4, 1, 129.90),
(2, 15, 2, 179.90),
(3, 26, 3, 129.90),
(4, 39, 1, 129.90),
(4, 40, 1, 99.90);

-- =====================================================
-- 12. ЗАКАЗЫ
-- =====================================================
INSERT INTO orders (user_id, order_number, total_amount, address_id, status_id, comment) VALUES
(2, 'ORD-20241201-0001', 518.80, 1, 4, 'Позвонить за 15 минут'),
(3, 'ORD-20241201-0002', 548.70, 3, 3, 'Оставьте у двери'),
(4, 'ORD-20241210-0003', 569.70, 4, 5, NULL),
(5, 'ORD-20241215-0004', 229.80, 5, 2, 'Доставить к 18:00'),
(2, 'ORD-20241220-0005', 899.00, 2, 1, NULL);

-- =====================================================
-- 13. ТОВАРЫ В ЗАКАЗАХ
-- =====================================================
INSERT INTO order_item (order_id, product_id, product_name, quantity, price) VALUES
(1, 1, 'Гречневая крупа "Мистраль"', 2, 89.90),
(1, 11, 'Молоко 3.2% "Домик в деревне"', 1, 89.90),
(1, 39, 'Шоколад Milka молочный', 1, 129.90),
(2, 4, 'Макароны Barilla Спагетти', 1, 129.90),
(2, 15, 'Сыр "Российский"', 2, 179.90),
(2, 26, 'Бананы', 1, 129.90),
(3, 26, 'Бананы', 2, 129.90),
(3, 27, 'Яблоки "Голден"', 1, 119.90),
(3, 39, 'Шоколад Milka молочный', 1, 129.90),
(4, 33, 'Вода "Святой источник" 1.5л', 2, 49.90),
(4, 34, 'Сок "Добрый" апельсиновый', 1, 129.90),
(5, 23, 'Говядина вырезка', 1, 899.00);

-- =====================================================
-- ПРОВЕРКА
-- =====================================================
SELECT '=== БАЗА ДАННЫХ НАПОЛНЕНА УСПЕШНО ===' AS message;
SELECT COUNT(*) as total_users FROM user;
SELECT COUNT(*) as total_products FROM product;
SELECT COUNT(*) as total_orders FROM orders;
SELECT COUNT(*) as total_addresses FROM address;
SELECT COUNT(*) as total_cities FROM city;
SELECT COUNT(*) as total_streets FROM street;

-- Проверка улиц по городам
SELECT 
    c.name AS city,
    COUNT(s.id) AS streets_count
FROM city c
LEFT JOIN street s ON s.city_id = c.id
WHERE c.name IN ('Оренбург', 'Орск', 'Новотроицк', 'Бузулук', 'Соль-Илецк', 'Москва', 'Санкт-Петербург')
GROUP BY c.id, c.name
ORDER BY c.name;

SELECT c.name as category, COUNT(*) as products_count 
FROM product p 
JOIN category c ON p.category_id = c.id 
GROUP BY p.category_id;

-- =====================================================
-- ВКЛЮЧАЕМ ПРОВЕРКИ ОБРАТНО
-- =====================================================
SET FOREIGN_KEY_CHECKS = 1;
SET SQL_SAFE_UPDATES = 1;

SELECT 'ГОТОВО!' AS message;