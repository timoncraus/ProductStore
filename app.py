from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
import mysql.connector
from mysql.connector import Error
import hashlib
import re
import time
import random
from functools import wraps
from datetime import datetime, timedelta
import secrets

app = Flask(__name__)
app.secret_key = secrets.token_hex(32)
app.permanent_session_lifetime = timedelta(hours=24)

# Конфигурация БД
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'tima120805',
    'database': 'product_store',
    'autocommit': False,
    'use_pure': True
}

def get_db_connection():
    """Получение соединения с БД"""
    try:
        conn = mysql.connector.connect(**db_config)
        return conn
    except Error as e:
        print(f"Ошибка подключения к БД: {e}")
        return None

# =====================================================
# ДЕКОРАТОРЫ И ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
# =====================================================

def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get('user_id'):
            flash('Необходимо войти в систему', 'warning')
            return redirect(url_for('login'))
        
        if session.get('role') != 'admin':
            flash('Доступ запрещён. Требуются права администратора.', 'danger')
            return redirect(url_for('index'))
        
        return f(*args, **kwargs)
    return decorated

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get('user_id'):
            flash('Пожалуйста, войдите в систему', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated

def validate_phone(phone):
    """Валидация номера телефона"""
    phone = re.sub(r'[\s\-\(\)]', '', phone)
    patterns = [
        r'^\+7\d{10}$',
        r'^8\d{10}$',
        r'^7\d{10}$',
        r'^9\d{9}$'
    ]
    for pattern in patterns:
        if re.match(pattern, phone):
            return True
    return False

def validate_email(email):
    """Валидация email"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_password_strength(password):
    """Проверка сложности пароля"""
    if len(password) < 9:
        return False, "Пароль должен содержать минимум 9 символов"
    if not re.search(r'[A-Za-z]', password):
        return False, "Пароль должен содержать буквы"
    if not re.search(r'\d', password):
        return False, "Пароль должен содержать цифры"
    if not re.search(r'[!@#$%^&*(),.?":{}|<>_\-+=]', password):
        return False, "Пароль должен содержать спецсимвол"
    if re.search(r'(password|123456|qwerty|admin)', password.lower()):
        return False, "Пароль слишком простой"
    return True, "OK"

failed_attempts = {}

def check_bruteforce(ip):
    if ip in failed_attempts:
        attempts, last_time = failed_attempts[ip]
        delays = {3: 5, 5: 10, 10: 15}
        if attempts >= 3:
            idx = min(attempts - 3, 2)
            delay = delays.get(3 + idx * 2, 15)
            if time.time() - last_time < delay:
                return False
    return True

def register_failed_attempt(ip):
    now = time.time()
    if ip in failed_attempts:
        count, _ = failed_attempts[ip]
        failed_attempts[ip] = (count + 1, now)
    else:
        failed_attempts[ip] = (1, now)

def generate_captcha():
    num1 = random.randint(1, 20)
    num2 = random.randint(1, 20)
    session['captcha_answer'] = num1 + num2
    return f"{num1} + {num2}"

def hash_password(password):
    salt = "product_store_salt_2024"
    return hashlib.sha256((password + salt).encode()).hexdigest()

def generate_order_number():
    return f"ORD-{datetime.now().strftime('%Y%m%d')}-{random.randint(1000, 9999)}"

# =====================================================
# ОСНОВНЫЕ МАРШРУТЫ
# =====================================================

@app.route('/')
def index():
    """Главная страница"""
    conn = get_db_connection()
    products = []
    categories = []
    
    if conn:
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute("""
                SELECT p.*, c.name as category_name
                FROM product p 
                JOIN category c ON p.category_id = c.id
                WHERE p.is_active = TRUE
                ORDER BY p.sales_count DESC, p.created_at DESC
                LIMIT 12
            """)
            products = cursor.fetchall()
            
            cursor.execute("""
                SELECT id, name, slug, image_url
                FROM category
                WHERE is_active = TRUE
                ORDER BY sort_order, name
                LIMIT 12
            """)
            categories = cursor.fetchall()
        except Error as e:
            print(f"Ошибка запроса: {e}")
        finally:
            conn.close()
    
    return render_template('index.html', products=products, categories=categories)

@app.route('/register', methods=['GET', 'POST'])
def register():
    """Регистрация пользователя"""
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        phone = request.form.get('phone', '').strip()
        password = request.form.get('password', '')
        password2 = request.form.get('password2', '')
        captcha = request.form.get('captcha', '')
        full_name = request.form.get('full_name', '')
        
        errors = []
        
        if not username or len(username) < 3:
            errors.append("Имя пользователя должно содержать минимум 3 символа")
        if not validate_email(email):
            errors.append("Неверный формат email")
        if not validate_phone(phone):
            errors.append("Неверный формат телефона. Пример: +79123456789")
        if password != password2:
            errors.append("Пароли не совпадают")
        
        valid_pwd, pwd_msg = validate_password_strength(password)
        if not valid_pwd:
            errors.append(pwd_msg)
        
        try:
            if int(captcha) != session.get('captcha_answer', 0):
                errors.append("Неверный ответ капчи")
        except ValueError:
            errors.append("Неверный ответ капчи")
        
        if errors:
            for error in errors:
                flash(error, 'danger')
            return redirect(url_for('register'))
        
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor()
            password_hash = hash_password(password)
            
            try:
                cursor.execute("""
                    INSERT INTO user (username, email, phone, password_hash, full_name, role)
                    VALUES (%s, %s, %s, %s, %s, 'user')
                """, (username, email, phone, password_hash, full_name))
                conn.commit()
                
                user_id = cursor.lastrowid
                cursor.execute("INSERT INTO cart (user_id) VALUES (%s)", (user_id,))
                conn.commit()
                
                flash('Регистрация успешна! Теперь вы можете войти.', 'success')
                return redirect(url_for('login'))
            except Error as e:
                if 'Duplicate' in str(e):
                    if 'username' in str(e):
                        flash('Пользователь с таким именем уже существует', 'danger')
                    elif 'email' in str(e):
                        flash('Пользователь с таким email уже существует', 'danger')
                    else:
                        flash('Пользователь с таким телефоном уже существует', 'danger')
                else:
                    flash(f'Ошибка регистрации: {str(e)}', 'danger')
            finally:
                conn.close()
    
    captcha_question = generate_captcha()
    return render_template('register.html', captcha_question=captcha_question)

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Вход в систему"""
    ip = request.remote_addr
    
    if not check_bruteforce(ip):
        flash('Слишком много попыток. Подождите 15 секунд.', 'danger')
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        username = request.form.get('username', '')
        password = request.form.get('password', '')
        
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor(dictionary=True)
            password_hash = hash_password(password)
            
            try:
                cursor.execute("""
                    SELECT * FROM user 
                    WHERE username = %s AND password_hash = %s AND is_active = TRUE
                """, (username, password_hash))
                
                user = cursor.fetchone()
                
                if user:
                    session.permanent = True
                    session['user_id'] = user['id']
                    session['username'] = user['username']
                    session['role'] = user['role']
                    
                    cursor.execute("UPDATE user SET last_login = NOW() WHERE id = %s", (user['id'],))
                    conn.commit()
                    
                    flash(f'Добро пожаловать, {user["username"]}!', 'success')
                    
                    if user['role'] == 'admin':
                        return redirect(url_for('admin_dashboard'))
                    return redirect(url_for('index'))
                else:
                    register_failed_attempt(ip)
                    flash('Неверное имя пользователя или пароль', 'danger')
            except Error as e:
                flash(f'Ошибка входа: {str(e)}', 'danger')
            finally:
                conn.close()
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Вы вышли из системы', 'info')
    return redirect(url_for('index'))

@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    """Профиль пользователя"""
    conn = get_db_connection()
    user = None
    orders = []
    addresses = []
    
    if conn:
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute("""
                SELECT id, username, email, phone, full_name, created_at, last_login
                FROM user WHERE id = %s
            """, (session['user_id'],))
            user = cursor.fetchone()
            
            if request.method == 'POST':
                full_name = request.form.get('full_name', '')
                phone = request.form.get('phone', '')
                email = request.form.get('email', '')
                
                if phone and not validate_phone(phone):
                    flash('Неверный формат телефона', 'danger')
                elif email and not validate_email(email):
                    flash('Неверный формат email', 'danger')
                else:
                    cursor.execute("""
                        UPDATE user 
                        SET full_name=%s, phone=%s, email=%s
                        WHERE id=%s
                    """, (full_name, phone, email, session['user_id']))
                    conn.commit()
                    flash('Профиль успешно обновлен', 'success')
                    return redirect(url_for('profile'))
            
            # Получаем адреса пользователя
            cursor.execute("""
                SELECT ua.*, 
                       s.name as street_name, c.name as city_name, 
                       r.name as region_name, co.name as country_name
                FROM user_address ua
                JOIN street s ON ua.street_id = s.id
                JOIN city c ON s.city_id = c.id
                JOIN region r ON c.region_id = r.id
                JOIN country co ON r.country_id = co.id
                WHERE ua.user_id = %s
                ORDER BY ua.is_default DESC, ua.created_at DESC
            """, (session['user_id'],))
            addresses = cursor.fetchall()
            
            # Получаем заказы
            cursor.execute("""
                SELECT o.*, os.name as status_name
                FROM orders o 
                JOIN order_status os ON o.status_id = os.id
                WHERE o.user_id = %s 
                ORDER BY o.created_at DESC 
                LIMIT 20
            """, (session['user_id'],))
            orders = cursor.fetchall()
            
        except Error as e:
            print(f"Ошибка: {e}")
            flash(f'Ошибка загрузки данных: {e}', 'danger')
        finally:
            conn.close()
    
    return render_template('user/profile.html', user=user, orders=orders, addresses=addresses)

# =====================================================
# КАТАЛОГ
# =====================================================

@app.route('/catalog')
def catalog():
    """Страница каталога"""
    category_id = request.args.get('category', type=int)
    search = request.args.get('search', '')
    page = request.args.get('page', 1, type=int)
    per_page = 24
    offset = (page - 1) * per_page
    
    conn = get_db_connection()
    products = []
    total = 0
    categories = []
    current_category = None
    
    if conn:
        cursor = conn.cursor(dictionary=True)
        
        query = """
            SELECT p.*, c.name as category_name
            FROM product p
            JOIN category c ON p.category_id = c.id
            WHERE p.is_active = TRUE
        """
        count_query = "SELECT COUNT(*) as total FROM product p WHERE p.is_active = TRUE"
        params = []
        
        if category_id:
            query += " AND p.category_id = %s"
            count_query += " AND category_id = %s"
            params.append(category_id)
            
            cursor.execute("SELECT * FROM category WHERE id = %s", (category_id,))
            current_category = cursor.fetchone()
        
        if search:
            query += " AND (p.name LIKE %s OR p.description LIKE %s)"
            count_query += " AND (name LIKE %s OR description LIKE %s)"
            search_param = f"%{search}%"
            params.extend([search_param, search_param])
        
        query += " ORDER BY p.sales_count DESC, p.created_at DESC LIMIT %s OFFSET %s"
        params.extend([per_page, offset])
        
        try:
            cursor.execute(query, params)
            products = cursor.fetchall()
            
            count_params = params[:-2] if params else []
            cursor.execute(count_query, count_params)
            total_row = cursor.fetchone()
            total = total_row['total'] if total_row else 0
            
            cursor.execute("""
                SELECT c.id, c.name, c.slug, c.image_url,
                    (SELECT COUNT(*) FROM product WHERE category_id = c.id AND is_active = TRUE) as product_count
                FROM category c
                WHERE c.is_active = TRUE
                ORDER BY c.sort_order, c.name
            """)
            categories = cursor.fetchall()
            
        except Error as e:
            print(f"Ошибка: {e}")
            flash(f'Ошибка загрузки каталога: {e}', 'danger')
        finally:
            conn.close()
    
    total_pages = (total + per_page - 1) // per_page if total > 0 else 1
    
    return render_template('user/catalog.html', 
                          products=products, 
                          categories=categories,
                          current_category=current_category,
                          total=total,
                          page=page,
                          total_pages=total_pages,
                          category_id=category_id,
                          search=search)

@app.route('/product/<int:product_id>')
def product_detail(product_id):
    """Детальная страница товара"""
    conn = get_db_connection()
    product = None
    in_wishlist = False
    
    if conn:
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute("""
                SELECT p.*, c.name as category_name, c.slug as category_slug
                FROM product p
                JOIN category c ON p.category_id = c.id
                WHERE p.id = %s AND p.is_active = TRUE
            """, (product_id,))
            product = cursor.fetchone()
            
            if product:
                # Убираем views_count, так как его нет в таблице
                # cursor.execute("UPDATE product SET views_count = views_count + 1 WHERE id = %s", (product_id,))
                # conn.commit()
                
                if session.get('user_id'):
                    cursor.execute("""
                        SELECT 1 FROM wishlist WHERE user_id = %s AND product_id = %s
                    """, (session['user_id'], product_id))
                    in_wishlist = cursor.fetchone() is not None
                
        except Error as e:
            print(f"Ошибка: {e}")
            flash(f'Ошибка загрузки товара: {e}', 'danger')
        finally:
            conn.close()
    
    if not product:
        flash('Товар не найден', 'danger')
        return redirect(url_for('catalog'))
    
    return render_template('user/product_detail.html', 
                          product=product, 
                          in_wishlist=in_wishlist)

# =====================================================
# КОРЗИНА
# =====================================================

@app.route('/cart')
@login_required
def view_cart():
    """Просмотр корзины"""
    conn = get_db_connection()
    cart_items = []
    total = 0
    
    if conn:
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute("""
                SELECT ci.id as cart_item_id, ci.product_id, ci.quantity, ci.price,
                       p.name, p.image_url, p.stock,
                       (ci.quantity * ci.price) as item_total
                FROM cart_item ci
                JOIN cart c ON ci.cart_id = c.id
                JOIN product p ON ci.product_id = p.id
                WHERE c.user_id = %s
            """, (session['user_id'],))
            cart_items = cursor.fetchall()
            
            for item in cart_items:
                total += item['item_total']
        except Error as e:
            flash(f'Ошибка загрузки корзины: {e}', 'danger')
        finally:
            conn.close()
    
    return render_template('user/cart.html', cart_items=cart_items, total=total)

@app.route('/cart/add', methods=['POST'])
@login_required
def add_to_cart():
    """Добавление товара в корзину"""
    product_id = request.form.get('product_id', type=int)
    quantity = request.form.get('quantity', 1, type=int)
    
    if not product_id:
        flash('Товар не найден', 'warning')
        return redirect(request.referrer or url_for('catalog'))
    
    if quantity < 1:
        quantity = 1
    
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute("SELECT id FROM cart WHERE user_id = %s", (session['user_id'],))
            cart = cursor.fetchone()
            cart_id = cart['id']
            
            cursor.execute("SELECT price FROM product WHERE id = %s", (product_id,))
            product = cursor.fetchone()
            price = product['price'] if product else 0
            
            cursor.execute("""
                INSERT INTO cart_item (cart_id, product_id, quantity, price)
                VALUES (%s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE quantity = quantity + %s
            """, (cart_id, product_id, quantity, price, quantity))
            conn.commit()
            flash('Товар добавлен в корзину', 'success')
        except Error as e:
            flash(f'Ошибка: {str(e)}', 'danger')
        finally:
            conn.close()
    
    return redirect(url_for('view_cart'))

@app.route('/cart/update', methods=['POST'])
@login_required
def update_cart():
    cart_item_id = request.form.get('cart_item_id', type=int)
    quantity = request.form.get('quantity', type=int)
    
    if cart_item_id and quantity and quantity > 0:
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor()
            try:
                cursor.execute("UPDATE cart_item SET quantity = %s WHERE id = %s", (quantity, cart_item_id))
                conn.commit()
                flash('Корзина обновлена', 'success')
            except Error as e:
                flash(f'Ошибка: {e}', 'danger')
            finally:
                conn.close()
    
    return redirect(url_for('view_cart'))

@app.route('/cart/remove/<int:item_id>')
@login_required
def remove_from_cart(item_id):
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        try:
            cursor.execute("DELETE FROM cart_item WHERE id = %s", (item_id,))
            conn.commit()
            flash('Товар удалён из корзины', 'info')
        except Error as e:
            flash(f'Ошибка: {e}', 'danger')
        finally:
            conn.close()
    
    return redirect(url_for('view_cart'))

# =====================================================
# ОФОРМЛЕНИЕ ЗАКАЗА
# =====================================================

@app.route('/checkout', methods=['GET', 'POST'])
@login_required
def checkout():
    """Оформление заказа"""
    conn = get_db_connection()
    cart_items = []
    total = 0
    user = None
    
    if conn:
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute("SELECT id, full_name, phone, address FROM user WHERE id = %s", (session['user_id'],))
            user = cursor.fetchone()
            
            cursor.execute("""
                SELECT ci.id as cart_item_id, ci.product_id, ci.quantity, ci.price,
                       p.name, p.image_url, p.stock,
                       (ci.quantity * ci.price) as item_total
                FROM cart_item ci
                JOIN cart c ON ci.cart_id = c.id
                JOIN product p ON ci.product_id = p.id
                WHERE c.user_id = %s
            """, (session['user_id'],))
            cart_items = cursor.fetchall()
            
            for item in cart_items:
                total += item['item_total']
            
            if not cart_items:
                flash('Корзина пуста', 'warning')
                return redirect(url_for('catalog'))
            
            if request.method == 'POST':
                delivery_address = request.form.get('delivery_address', '')
                recipient_name = request.form.get('recipient_name', '')
                recipient_phone = request.form.get('recipient_phone', '')
                comment = request.form.get('comment', '')
                
                if not delivery_address:
                    flash('Введите адрес доставки', 'danger')
                    return redirect(url_for('checkout'))
                
                if not recipient_name:
                    recipient_name = user['full_name'] if user else ''
                if not recipient_phone:
                    recipient_phone = user['phone'] if user else ''
                
                order_number = generate_order_number()
                
                cursor.execute("""
                    INSERT INTO orders (user_id, order_number, total_amount, delivery_address, 
                                       recipient_name, recipient_phone, comment)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, (session['user_id'], order_number, total, delivery_address, 
                      recipient_name, recipient_phone, comment))
                
                order_id = cursor.lastrowid
                
                for item in cart_items:
                    cursor.execute("""
                        INSERT INTO order_item (order_id, product_id, product_name, quantity, price)
                        VALUES (%s, %s, %s, %s, %s)
                    """, (order_id, item['product_id'], item['name'], 
                          item['quantity'], item['price']))
                    
                    cursor.execute("""
                        UPDATE product 
                        SET stock = stock - %s, sales_count = sales_count + %s
                        WHERE id = %s
                    """, (item['quantity'], item['quantity'], item['product_id']))
                
                cursor.execute("DELETE FROM cart_item WHERE cart_id = (SELECT id FROM cart WHERE user_id = %s)",
                              (session['user_id'],))
                
                conn.commit()
                flash(f'Заказ #{order_number} успешно оформлен!', 'success')
                return redirect(url_for('profile'))
                
        except Error as e:
            conn.rollback()
            flash(f'Ошибка оформления заказа: {str(e)}', 'danger')
        finally:
            conn.close()
    
    return render_template('user/checkout.html', 
                          cart_items=cart_items, 
                          total=total,
                          user=user)

# =====================================================
# ИЗБРАННОЕ
# =====================================================

@app.route('/wishlist')
@login_required
def wishlist():
    conn = get_db_connection()
    products = []
    
    if conn:
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute("""
                SELECT p.*, w.added_at
                FROM wishlist w
                JOIN product p ON w.product_id = p.id
                WHERE w.user_id = %s
                ORDER BY w.added_at DESC
            """, (session['user_id'],))
            products = cursor.fetchall()
        except Error as e:
            flash(f'Ошибка: {e}', 'danger')
        finally:
            conn.close()
    
    return render_template('user/wishlist.html', products=products)

@app.route('/wishlist/add/<int:product_id>')
@login_required
def add_to_wishlist(product_id):
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO wishlist (user_id, product_id)
                VALUES (%s, %s)
            """, (session['user_id'], product_id))
            conn.commit()
            flash('Товар добавлен в избранное', 'success')
        except Error as e:
            if 'Duplicate' not in str(e):
                flash(f'Ошибка: {e}', 'danger')
        finally:
            conn.close()
    
    return redirect(request.referrer or url_for('catalog'))

@app.route('/wishlist/remove/<int:product_id>')
@login_required
def remove_from_wishlist(product_id):
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        try:
            cursor.execute("""
                DELETE FROM wishlist WHERE user_id = %s AND product_id = %s
            """, (session['user_id'], product_id))
            conn.commit()
            flash('Товар удален из избранного', 'info')
        except Error as e:
            flash(f'Ошибка: {e}', 'danger')
        finally:
            conn.close()
    
    return redirect(request.referrer or url_for('wishlist'))

# =====================================================
# АДМИНКА
# =====================================================

@app.route('/admin')
@admin_required
def admin_dashboard():
    conn = get_db_connection()
    stats = {
        'products_count': 0,
        'users_count': 0,
        'orders_today': 0,
        'orders_total': 0,
        'revenue_today': 0,
        'revenue_total': 0,
        'new_users_today': 0,
        'low_stock_products': 0,
    }
    recent_orders = []
    recent_users = []
    
    if conn:
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute("SELECT COUNT(*) as count FROM product WHERE is_active = TRUE")
            stats['products_count'] = cursor.fetchone()['count']
            
            cursor.execute("SELECT COUNT(*) as count FROM user WHERE role = 'user' AND is_active = TRUE")
            stats['users_count'] = cursor.fetchone()['count']
            
            cursor.execute("""
                SELECT COUNT(*) as count, COALESCE(SUM(total_amount), 0) as total
                FROM orders WHERE DATE(created_at) = CURDATE()
            """)
            today = cursor.fetchone()
            stats['orders_today'] = today['count'] if today else 0
            stats['revenue_today'] = today['total'] if today else 0
            
            cursor.execute("""
                SELECT COUNT(*) as count, COALESCE(SUM(total_amount), 0) as total
                FROM orders WHERE status_id NOT IN (6)
            """)
            total_data = cursor.fetchone()
            stats['orders_total'] = total_data['count'] if total_data else 0
            stats['revenue_total'] = total_data['total'] if total_data else 0
            
            cursor.execute("SELECT COUNT(*) as count FROM user WHERE DATE(created_at) = CURDATE()")
            stats['new_users_today'] = cursor.fetchone()['count']
            
            cursor.execute("SELECT COUNT(*) as count FROM product WHERE stock <= 10 AND stock > 0")
            stats['low_stock_products'] = cursor.fetchone()['count']
            
            cursor.execute("""
                SELECT o.*, u.username, os.name as status_name
                FROM orders o
                JOIN user u ON o.user_id = u.id
                JOIN order_status os ON o.status_id = os.id
                ORDER BY o.created_at DESC
                LIMIT 10
            """)
            recent_orders = cursor.fetchall()
            
            cursor.execute("""
                SELECT id, username, email, created_at
                FROM user
                WHERE role = 'user'
                ORDER BY created_at DESC
                LIMIT 10
            """)
            recent_users = cursor.fetchall()
            
        except Error as e:
            print(f"Ошибка: {e}")
        finally:
            conn.close()
    
    return render_template('admin/dashboard.html', 
                          stats=stats, 
                          recent_orders=recent_orders,
                          recent_users=recent_users)

@app.route('/admin/tables')
@admin_required
def list_tables():
    conn = get_db_connection()
    tables = []
    
    if conn:
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute("""
                SELECT TABLE_NAME, TABLE_ROWS
                FROM information_schema.TABLES 
                WHERE TABLE_SCHEMA = 'product_store'
                ORDER BY TABLE_NAME
            """)
            tables = cursor.fetchall()
        except Error as e:
            flash(f'Ошибка получения списка таблиц: {e}', 'danger')
        finally:
            conn.close()
    
    return render_template('admin/tables.html', tables=tables)

@app.route('/admin/table/<table_name>')
@admin_required
def view_table(table_name):
    page = request.args.get('page', 1, type=int)
    per_page = 20
    offset = (page - 1) * per_page
    
    conn = get_db_connection()
    rows = []
    columns = []
    total_rows = 0
    
    if conn:
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute(f"SELECT COUNT(*) as total FROM `{table_name}`")
            result = cursor.fetchone()
            total_rows = result['total'] if result else 0
            
            cursor.execute(f"SELECT * FROM `{table_name}` LIMIT %s OFFSET %s", (per_page, offset))
            rows = cursor.fetchall()
            
            cursor.execute(f"DESCRIBE `{table_name}`")
            columns = cursor.fetchall()
            
        except Error as e:
            flash(f'Ошибка: {e}', 'danger')
        finally:
            conn.close()
    
    total_pages = (total_rows + per_page - 1) // per_page if total_rows > 0 else 1
    
    return render_template('admin/edit_row.html', 
                          table=table_name, 
                          rows=rows, 
                          columns=columns,
                          page=page,
                          total_pages=total_pages,
                          total_rows=total_rows)

@app.route('/admin/table/<table_name>/add', methods=['POST'])
@admin_required
def add_row(table_name):
    data = {k: v for k, v in request.form.items() if v and v != ''}
    if 'id' in data:
        del data['id']
    
    if not data:
        flash('Нет данных для добавления', 'danger')
        return redirect(url_for('view_table', table_name=table_name))
    
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        columns = ', '.join([f'`{k}`' for k in data.keys()])
        placeholders = ', '.join(['%s'] * len(data))
        values = list(data.values())
        
        try:
            cursor.execute(f"INSERT INTO `{table_name}` ({columns}) VALUES ({placeholders})", values)
            conn.commit()
            flash(f'Запись успешно добавлена в таблицу {table_name}', 'success')
        except Error as e:
            flash(f'Ошибка добавления: {str(e)}', 'danger')
        finally:
            conn.close()
    
    return redirect(url_for('view_table', table_name=table_name))

@app.route('/admin/table/<table_name>/edit/<int:row_id>', methods=['POST'])
@admin_required
def edit_row(table_name, row_id):
    data = {k: v for k, v in request.form.items() if k != 'id'}
    
    if not data:
        flash('Нет данных для обновления', 'danger')
        return redirect(url_for('view_table', table_name=table_name))
    
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        set_clause = ', '.join([f'`{k}`=%s' for k in data.keys()])
        values = list(data.values()) + [row_id]
        
        try:
            cursor.execute(f"UPDATE `{table_name}` SET {set_clause} WHERE id=%s", values)
            conn.commit()
            flash(f'Запись #{row_id} успешно обновлена', 'success')
        except Error as e:
            flash(f'Ошибка обновления: {str(e)}', 'danger')
        finally:
            conn.close()
    
    return redirect(url_for('view_table', table_name=table_name))

@app.route('/admin/table/<table_name>/delete/<int:row_id>')
@admin_required
def delete_row(table_name, row_id):
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        try:
            cursor.execute(f"DELETE FROM `{table_name}` WHERE id=%s", (row_id,))
            conn.commit()
            flash(f'Запись #{row_id} удалена', 'success')
        except Error as e:
            flash(f'Ошибка удаления: {str(e)}', 'danger')
        finally:
            conn.close()
    
    return redirect(url_for('view_table', table_name=table_name))

@app.route('/admin/products')
@admin_required
def admin_products():
    conn = get_db_connection()
    products = []
    
    if conn:
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute("""
                SELECT p.*, c.name as category_name
                FROM product p
                LEFT JOIN category c ON p.category_id = c.id
                ORDER BY p.created_at DESC
            """)
            products = cursor.fetchall()
        except Error as e:
            flash(f'Ошибка: {e}', 'danger')
        finally:
            conn.close()
    
    return render_template('admin/products.html', products=products)

@app.route('/admin/products/add', methods=['GET', 'POST'])
@admin_required
def admin_products_add():
    conn = get_db_connection()
    categories = []
    
    if conn:
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute("SELECT id, name FROM category WHERE is_active = TRUE ORDER BY name")
            categories = cursor.fetchall()
        except Error as e:
            flash(f'Ошибка: {e}', 'danger')
        finally:
            conn.close()
    
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        slug = request.form.get('slug', name.lower().replace(' ', '-').replace('ё', 'е'))
        description = request.form.get('description', '')
        price = request.form.get('price', type=float)
        old_price = request.form.get('old_price', type=float) or None
        category_id = request.form.get('category_id', type=int)
        stock = request.form.get('stock', type=int, default=0)
        unit = request.form.get('unit', 'шт')
        is_new = request.form.get('is_new') == 'on'
        is_hit = request.form.get('is_hit') == 'on'
        
        if not name or not price or not category_id:
            flash('Заполните обязательные поля (Название, Цена, Категория)', 'danger')
        else:
            conn = get_db_connection()
            if conn:
                cursor = conn.cursor()
                try:
                    cursor.execute("""
                        INSERT INTO product (name, slug, description, price, old_price, 
                                           category_id, stock, unit, is_new, is_hit)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """, (name, slug, description, price, old_price, 
                          category_id, stock, unit, is_new, is_hit))
                    conn.commit()
                    flash(f'Товар "{name}" успешно добавлен!', 'success')
                    return redirect(url_for('admin_products'))
                except Error as e:
                    conn.rollback()
                    flash(f'Ошибка: {str(e)}', 'danger')
                finally:
                    conn.close()
    
    return render_template('admin/product_add.html', categories=categories)

@app.route('/admin/products/edit/<int:product_id>', methods=['GET', 'POST'])
@admin_required
def admin_products_edit(product_id):
    conn = get_db_connection()
    product = None
    categories = []
    
    if conn:
        cursor = conn.cursor(dictionary=True)
        try:
            if request.method == 'POST':
                name = request.form.get('name', '').strip()
                slug = request.form.get('slug', '')
                description = request.form.get('description', '')
                price = request.form.get('price', type=float)
                old_price = request.form.get('old_price', type=float) or None
                category_id = request.form.get('category_id', type=int)
                stock = request.form.get('stock', type=int, default=0)
                unit = request.form.get('unit', 'шт')
                is_active = request.form.get('is_active') == 'on'
                is_new = request.form.get('is_new') == 'on'
                is_hit = request.form.get('is_hit') == 'on'
                
                cursor.execute("""
                    UPDATE product 
                    SET name=%s, slug=%s, description=%s, price=%s, old_price=%s,
                        category_id=%s, stock=%s, unit=%s,
                        is_active=%s, is_new=%s, is_hit=%s
                    WHERE id=%s
                """, (name, slug, description, price, old_price,
                      category_id, stock, unit,
                      is_active, is_new, is_hit, product_id))
                conn.commit()
                flash('Товар обновлён', 'success')
                return redirect(url_for('admin_products'))
            
            cursor.execute("SELECT * FROM product WHERE id = %s", (product_id,))
            product = cursor.fetchone()
            
            cursor.execute("SELECT id, name FROM category WHERE is_active = TRUE ORDER BY name")
            categories = cursor.fetchall()
            
        except Error as e:
            flash(f'Ошибка: {e}', 'danger')
        finally:
            conn.close()
    
    if not product:
        flash('Товар не найден', 'danger')
        return redirect(url_for('admin_products'))
    
    return render_template('admin/product_edit.html', product=product, categories=categories)

@app.route('/admin/products/delete/<int:product_id>')
@admin_required
def admin_products_delete(product_id):
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        try:
            cursor.execute("DELETE FROM product WHERE id = %s", (product_id,))
            conn.commit()
            flash('Товар удалён', 'success')
        except Error as e:
            flash(f'Ошибка: {e}', 'danger')
        finally:
            conn.close()
    
    return redirect(url_for('admin_products'))

@app.route('/admin/categories')
@admin_required
def admin_categories():
    conn = get_db_connection()
    categories = []
    
    if conn:
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute("""
                SELECT c.*, 
                       (SELECT COUNT(*) FROM product WHERE category_id = c.id) as products_count,
                       parent.name as parent_name
                FROM category c
                LEFT JOIN category parent ON c.parent_id = parent.id
                ORDER BY c.sort_order, c.name
            """)
            categories = cursor.fetchall()
        except Error as e:
            flash(f'Ошибка: {e}', 'danger')
        finally:
            conn.close()
    
    return render_template('admin/categories.html', categories=categories)

@app.route('/admin/categories/add', methods=['POST'])
@admin_required
def admin_category_add():
    name = request.form.get('name', '').strip()
    slug = request.form.get('slug', name.lower().replace(' ', '-').replace('ё', 'е'))
    parent_id = request.form.get('parent_id', type=int) or None
    sort_order = request.form.get('sort_order', type=int, default=0)
    
    if not name:
        flash('Введите название категории', 'danger')
    else:
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor()
            try:
                cursor.execute("""
                    INSERT INTO category (name, slug, parent_id, sort_order, is_active)
                    VALUES (%s, %s, %s, %s, 1)
                """, (name, slug, parent_id, sort_order))
                conn.commit()
                flash(f'Категория "{name}" добавлена', 'success')
            except Error as e:
                flash(f'Ошибка: {e}', 'danger')
            finally:
                conn.close()
    
    return redirect(url_for('admin_categories'))

@app.route('/admin/categories/delete/<int:category_id>')
@admin_required
def admin_category_delete(category_id):
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        try:
            cursor.execute("DELETE FROM category WHERE id = %s", (category_id,))
            conn.commit()
            flash('Категория удалена', 'success')
        except Error as e:
            flash(f'Ошибка: {e}', 'danger')
        finally:
            conn.close()
    
    return redirect(url_for('admin_categories'))

@app.route('/admin/orders')
@admin_required
def admin_orders():
    conn = get_db_connection()
    orders = []
    statuses = []
    
    if conn:
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute("""
                SELECT o.*, u.username, u.email, u.phone, os.name as status_name
                FROM orders o
                JOIN user u ON o.user_id = u.id
                JOIN order_status os ON o.status_id = os.id
                ORDER BY o.created_at DESC
            """)
            orders = cursor.fetchall()
            
            cursor.execute("SELECT * FROM order_status ORDER BY id")
            statuses = cursor.fetchall()
        except Error as e:
            flash(f'Ошибка: {e}', 'danger')
        finally:
            conn.close()
    
    return render_template('admin/orders.html', orders=orders, statuses=statuses)

@app.route('/admin/orders/<int:order_id>/status', methods=['POST'])
@admin_required
def admin_order_update_status(order_id):
    status_id = request.form.get('status_id', type=int)
    
    if not status_id:
        flash('Выберите статус', 'danger')
        return redirect(url_for('admin_orders'))
    
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        try:
            cursor.execute("UPDATE orders SET status_id = %s WHERE id = %s", (status_id, order_id))
            conn.commit()
            flash('Статус заказа обновлён', 'success')
        except Error as e:
            flash(f'Ошибка: {str(e)}', 'danger')
        finally:
            conn.close()
    
    return redirect(url_for('admin_orders'))

@app.route('/admin/users')
@admin_required
def admin_users():
    conn = get_db_connection()
    users = []
    
    if conn:
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute("""
                SELECT u.*, 
                       (SELECT COUNT(*) FROM orders WHERE user_id = u.id) as orders_count,
                       (SELECT COALESCE(SUM(total_amount), 0) FROM orders WHERE user_id = u.id) as total_spent
                FROM user u
                ORDER BY u.created_at DESC
            """)
            users = cursor.fetchall()
        except Error as e:
            flash(f'Ошибка: {e}', 'danger')
        finally:
            conn.close()
    
    return render_template('admin/users.html', users=users)

@app.route('/admin/users/toggle/<int:user_id>')
@admin_required
def admin_user_toggle(user_id):
    if user_id == session['user_id']:
        flash('Нельзя заблокировать самого себя', 'danger')
        return redirect(url_for('admin_users'))
    
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        try:
            cursor.execute("UPDATE user SET is_active = NOT is_active WHERE id = %s", (user_id,))
            conn.commit()
            flash('Статус пользователя изменен', 'success')
        except Error as e:
            flash(f'Ошибка: {e}', 'danger')
        finally:
            conn.close()
    
    return redirect(url_for('admin_users'))

# =====================================================
# API
# =====================================================

@app.route('/api/search')
def api_search():
    query = request.args.get('q', '')
    if len(query) < 2:
        return jsonify([])
    
    conn = get_db_connection()
    results = []
    
    if conn:
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute("""
                SELECT id, name, price, slug, image_url
                FROM product
                WHERE name LIKE %s AND is_active = TRUE
                LIMIT 10
            """, (f"%{query}%",))
            results = cursor.fetchall()
        except Error as e:
            print(f"Ошибка: {e}")
        finally:
            conn.close()
    
    return jsonify(results)

@app.route('/api/cart/count')
@login_required
def api_cart_count():
    conn = get_db_connection()
    count = 0
    
    if conn:
        cursor = conn.cursor()
        try:
            cursor.execute("""
                SELECT COALESCE(SUM(ci.quantity), 0) as total
                FROM cart_item ci
                JOIN cart c ON ci.cart_id = c.id
                WHERE c.user_id = %s
            """, (session['user_id'],))
            result = cursor.fetchone()
            count = result[0] if result else 0
        except Error as e:
            print(f"Ошибка: {e}")
        finally:
            conn.close()
    
    return jsonify({'count': count})

# =====================================================
# УПРАВЛЕНИЕ АДРЕСАМИ
# =====================================================

@app.route('/profile/address/add', methods=['POST'])
@login_required
def add_delivery_address():
    """Добавление адреса доставки"""
    country_name = request.form.get('country', '').strip()
    region_name = request.form.get('region', '').strip()
    city_name = request.form.get('city', '').strip()
    street_name = request.form.get('street', '').strip()
    house = request.form.get('house', '').strip()
    apartment = request.form.get('apartment', '').strip()
    entrance = request.form.get('entrance', '')
    floor = request.form.get('floor', type=int) or None
    postal_code = request.form.get('postal_code', '')
    is_default = request.form.get('is_default') == 'on'
    
    if not all([country_name, region_name, city_name, street_name, house]):
        flash('Заполните обязательные поля (Страна, Регион, Город, Улица, Дом)', 'danger')
        return redirect(url_for('profile'))
    
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        try:
            # Получаем или создаем страну
            cursor.execute("SELECT id FROM country WHERE name = %s", (country_name,))
            country = cursor.fetchone()
            if not country:
                cursor.execute("INSERT INTO country (name) VALUES (%s)", (country_name,))
                conn.commit()
                country_id = cursor.lastrowid
            else:
                country_id = country[0]
            
            # Получаем или создаем регион
            cursor.execute("SELECT id FROM region WHERE name = %s AND country_id = %s", (region_name, country_id))
            region = cursor.fetchone()
            if not region:
                cursor.execute("INSERT INTO region (name, country_id) VALUES (%s, %s)", (region_name, country_id))
                conn.commit()
                region_id = cursor.lastrowid
            else:
                region_id = region[0]
            
            # Получаем или создаем город
            cursor.execute("SELECT id FROM city WHERE name = %s AND region_id = %s", (city_name, region_id))
            city = cursor.fetchone()
            if not city:
                cursor.execute("INSERT INTO city (name, region_id) VALUES (%s, %s)", (city_name, region_id))
                conn.commit()
                city_id = cursor.lastrowid
            else:
                city_id = city[0]
            
            # Получаем или создаем улицу
            cursor.execute("SELECT id FROM street WHERE name = %s AND city_id = %s", (street_name, city_id))
            street = cursor.fetchone()
            if not street:
                cursor.execute("INSERT INTO street (name, city_id) VALUES (%s, %s)", (street_name, city_id))
                conn.commit()
                street_id = cursor.lastrowid
            else:
                street_id = street[0]
            
            # Если адрес по умолчанию - сбрасываем остальные
            if is_default:
                cursor.execute("UPDATE user_address SET is_default = FALSE WHERE user_id = %s", (session['user_id'],))
            
            # Добавляем адрес
            cursor.execute("""
                INSERT INTO user_address (user_id, street_id, house, apartment, entrance, floor, postal_code, is_default)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (session['user_id'], street_id, house, apartment, entrance, floor, postal_code, is_default))
            conn.commit()
            
            flash('Адрес успешно добавлен!', 'success')
        except Error as e:
            conn.rollback()
            flash(f'Ошибка добавления адреса: {str(e)}', 'danger')
        finally:
            conn.close()
    
    return redirect(url_for('profile'))

@app.route('/profile/address/delete/<int:address_id>')
@login_required
def delete_delivery_address(address_id):
    """Удаление адреса доставки"""
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        try:
            cursor.execute("DELETE FROM user_address WHERE id = %s AND user_id = %s", (address_id, session['user_id']))
            conn.commit()
            flash('Адрес удален', 'success')
        except Error as e:
            flash(f'Ошибка: {e}', 'danger')
        finally:
            conn.close()
    
    return redirect(url_for('profile'))

@app.route('/profile/address/set-default/<int:address_id>')
@login_required
def set_default_address(address_id):
    """Установка адреса по умолчанию"""
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        try:
            cursor.execute("UPDATE user_address SET is_default = FALSE WHERE user_id = %s", (session['user_id'],))
            cursor.execute("UPDATE user_address SET is_default = TRUE WHERE id = %s AND user_id = %s", (address_id, session['user_id']))
            conn.commit()
            flash('Адрес установлен как основной', 'success')
        except Error as e:
            flash(f'Ошибка: {e}', 'danger')
        finally:
            conn.close()
    
    return redirect(url_for('profile'))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)