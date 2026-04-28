from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from helpers import *

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
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
                SELECT id, name, image_url
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


@main_bp.route('/register', methods=['GET', 'POST'])
def register():
    """Регистрация пользователя"""
    if request.method == 'GET':
        session.pop('_flashes', None)
    
    if request.method == 'POST':
        # Сохраняем введенные данные
        form_data = {
            'username': request.form.get('username', '').strip(),
            'email': request.form.get('email', '').strip(),
            'phone': request.form.get('phone', '').strip(),
            'first_name': request.form.get('first_name', '').strip(),
            'last_name': request.form.get('last_name', '').strip()
        }
        
        username = form_data['username']
        email = form_data['email']
        phone = form_data['phone']
        password = request.form.get('password', '')
        password2 = request.form.get('password2', '')
        captcha = request.form.get('captcha', '')
        
        errors = []
        
        # Валидация
        if not username or len(username) < 3:
            errors.append("Имя пользователя должно содержать минимум 3 символа")
        if not validate_email(email):
            errors.append("Неверный формат email")
        if not validate_phone(phone):
            errors.append("Неверный формат телефона. Пример: +79123456789")
        if password != password2:
            errors.append("Пароли не совпадают")
        
        # Проверка сложности пароля
        valid_pwd, pwd_msg = validate_password_strength(password)
        if not valid_pwd:
            errors.append(pwd_msg)
        
        # Проверка капчи
        if not verify_captcha(captcha):
            errors.append("Неверный код с картинки")
        
        if errors:
            for error in errors:
                flash(error, 'danger')
            captcha_image = get_captcha_image()
            return render_template('register.html', 
                                 captcha_image=captcha_image, 
                                 form_data=form_data)
        
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor()
            password_hash = hash_password(password)
            
            try:
                # Используем first_name и last_name вместо full_name
                cursor.execute("""
                    INSERT INTO user (username, email, phone, password_hash, first_name, last_name, role)
                    VALUES (%s, %s, %s, %s, %s, %s, 'user')
                """, (username, email, phone, password_hash, form_data['first_name'], form_data['last_name']))
                conn.commit()
                
                user_id = cursor.lastrowid
                cursor.execute("INSERT INTO cart (user_id) VALUES (%s)", (user_id,))
                conn.commit()
                
                flash('Регистрация успешна! Теперь вы можете войти.', 'success')
                return redirect(url_for('main.login'))
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
                captcha_image = get_captcha_image()
                return render_template('register.html', 
                                     captcha_image=captcha_image, 
                                     form_data=form_data)
            finally:
                conn.close()
    
    captcha_image = get_captcha_image()
    return render_template('register.html', captcha_image=captcha_image, form_data=None)


@main_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Вход в систему с защитой от Brute Force"""
    ip = request.remote_addr
    
    # Периодическая очистка старых записей
    cleanup_old_attempts()
    
    # POST запрос - обрабатываем отправку формы
    if request.method == 'POST':
        # Сохраняем введенные данные в сессию
        session['login_form_data'] = {'username': request.form.get('username', '')}
        
        # Проверяем блокировку
        attempts_info = get_attempts_info(ip)
        
        if attempts_info['is_blocked']:
            flash(f'Доступ заблокирован на {attempts_info["remaining"]} секунд. Подождите и попробуйте снова.', 'danger')
            # ВАЖНО: редирект на GET, чтобы избежать повторной отправки
            return redirect(url_for('main.login'))
        
        username = request.form.get('username', '')
        password = request.form.get('password', '')
        captcha = request.form.get('captcha', '')
        
        # Проверка капчи
        if not verify_captcha(captcha):
            delay = register_failed_attempt(ip)
            attempts_info = get_attempts_info(ip)
            flash('Неверный код с картинки', 'danger')
            
            if delay > 0:
                flash(f'Предупреждение: после {attempts_info["count"]} неудачных попыток вход будет заблокирован на {delay} секунд.', 'warning')
            
            # ВАЖНО: редирект на GET
            return redirect(url_for('main.login'))
        
        # Проверка логина и пароля
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
                    # Успешный вход
                    reset_bruteforce(ip)
                    session.pop('login_form_data', None)
                    
                    session.permanent = True
                    session['user_id'] = user['id']
                    session['username'] = user['username']
                    session['role'] = user['role']
                    
                    cursor.execute("UPDATE user SET last_login = NOW() WHERE id = %s", (user['id'],))
                    conn.commit()
                    
                    flash(f'Добро пожаловать, {user["username"]}!', 'success')
                    
                    if user['role'] == 'admin':
                        return redirect(url_for('admin.dashboard.dashboard'))
                    return redirect(url_for('main.index'))
                else:
                    # Неправильный логин или пароль
                    delay = register_failed_attempt(ip)
                    attempts_info = get_attempts_info(ip)
                    flash('Неверное имя пользователя или пароль', 'danger')
                    
                    if delay > 0:
                        flash(f'Предупреждение: после {attempts_info["count"]} неудачных попыток вход будет заблокирован на {delay} секунд.', 'warning')
                    
                    # ВАЖНО: редирект на GET
                    return redirect(url_for('main.login'))
            except Error as e:
                flash(f'Ошибка входа: {str(e)}', 'danger')
                return redirect(url_for('main.login'))
            finally:
                conn.close()
    
    # GET запрос - просто показываем форму
    if request.method == 'GET':
        # Получаем текущий статус блокировки
        attempts_info = get_attempts_info(ip)
        wait_time = attempts_info['remaining'] if attempts_info['is_blocked'] else 0
        
        # Отладочная информация (уберете после тестирования)
        print(f"DEBUG GET: IP {ip}, attempts={attempts_info['count']}, blocked={attempts_info['is_blocked']}, wait={wait_time}")
        
        captcha_image = get_captcha_image()
        return render_template('login.html', 
                             captcha_image=captcha_image, 
                             form_data=session.get('login_form_data', None),
                             wait_time=wait_time,
                             attempts_count=attempts_info['count'])


@main_bp.route('/logout')
def logout():
    session.clear()
    flash('Вы вышли из системы', 'info')
    return redirect(url_for('main.index'))


@main_bp.route('/refresh-captcha', methods=['POST'])
def refresh_captcha():
    """Обновление капчи"""
    try:
        captcha_image = get_captcha_image()
        return jsonify({'captcha_image': captcha_image})
    except Exception as e:
        print(f"Ошибка при генерации капчи: {e}")
        return jsonify({'error': 'Failed to generate captcha'}), 500