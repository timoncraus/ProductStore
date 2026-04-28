from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from helpers import *
from decorators import *

profile_bp = Blueprint('profile', __name__)

@profile_bp.route('/profile', methods=['GET', 'POST'])
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
                SELECT id, username, first_name, last_name, email, phone, created_at, last_login
                FROM user WHERE id = %s
            """, (session['user_id'],))
            user = cursor.fetchone()
            
            if request.method == 'POST':
                first_name = request.form.get('first_name', '').strip()
                last_name = request.form.get('last_name', '').strip()
                username = request.form.get('username', '').strip()
                phone = request.form.get('phone', '').strip()
                email = request.form.get('email', '').strip()
                
                errors = []
                if not username or len(username) < 3:
                    errors.append("Имя пользователя должно содержать минимум 3 символа")
                if phone and not validate_phone(phone):
                    errors.append('Неверный формат телефона')
                if email and not validate_email(email):
                    errors.append('Неверный формат email')
                
                if errors:
                    for error in errors:
                        flash(error, 'danger')
                else:
                    try:
                        cursor.execute("""
                            UPDATE user 
                            SET first_name=%s, last_name=%s, username=%s, phone=%s, email=%s
                            WHERE id=%s
                        """, (first_name, last_name, username, phone, email, session['user_id']))
                        conn.commit()
                        session['username'] = username
                        flash('Профиль успешно обновлен', 'success')
                        return redirect(url_for('profile.profile'))
                    except Error as e:
                        if 'Duplicate' in str(e):
                            flash('Пользователь с таким именем или email уже существует', 'danger')
                        else:
                            flash(f'Ошибка: {str(e)}', 'danger')
            
            # Получаем адреса пользователя
            cursor.execute("""
                SELECT a.*, 
                       s.name as street_name, 
                       c.name as city_name, 
                       r.name as region_name, 
                       co.name as country_name
                FROM address a
                JOIN street s ON a.street_id = s.id
                JOIN city c ON s.city_id = c.id
                JOIN region r ON c.region_id = r.id
                JOIN country co ON r.country_id = co.id
                WHERE a.user_id = %s
                ORDER BY a.is_default DESC, a.created_at DESC
            """, (session['user_id'],))
            addresses = cursor.fetchall()
            
            # Получаем заказы
            cursor.execute("""
                SELECT o.*, os.name as status_name,
                       CONCAT(co.name, ', ', r.name, ', ', c.name, ', ул. ', s.name, ', д. ', a.house,
                              IF(a.apartment IS NOT NULL AND a.apartment != '', CONCAT(', кв. ', a.apartment), ''),
                              IF(a.entrance IS NOT NULL AND a.entrance != '', CONCAT(', под. ', a.entrance), ''),
                              IF(a.floor IS NOT NULL, CONCAT(', эт. ', a.floor), ''),
                              IF(a.postal_code IS NOT NULL AND a.postal_code != '', CONCAT(', ', a.postal_code), '')) as full_address
                FROM orders o 
                JOIN order_status os ON o.status_id = os.id
                JOIN address a ON o.address_id = a.id
                JOIN street s ON a.street_id = s.id
                JOIN city c ON s.city_id = c.id
                JOIN region r ON c.region_id = r.id
                JOIN country co ON r.country_id = co.id
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


# API для автодополнения адресов
@profile_bp.route('/api/search-country')
def api_search_country():
    query = request.args.get('q', '').strip()
    if len(query) < 2:
        return jsonify([])
    
    conn = get_db_connection()
    results = []
    if conn:
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute("""
                SELECT id, name FROM country 
                WHERE name LIKE %s 
                ORDER BY name LIMIT 10
            """, (f'%{query}%',))
            results = cursor.fetchall()
        except Error as e:
            print(f"Ошибка: {e}")
        finally:
            conn.close()
    return jsonify(results)


@profile_bp.route('/api/search-region')
def api_search_region():
    query = request.args.get('q', '').strip()
    country_id = request.args.get('country_id', type=int)
    
    if len(query) < 2:
        return jsonify([])
    
    conn = get_db_connection()
    results = []
    if conn:
        cursor = conn.cursor(dictionary=True)
        try:
            sql = """
                SELECT id, name, country_id FROM region 
                WHERE name LIKE %s
            """
            params = [f'%{query}%']
            if country_id:
                sql += " AND country_id = %s"
                params.append(country_id)
            sql += " ORDER BY name LIMIT 10"
            
            cursor.execute(sql, params)
            results = cursor.fetchall()
        except Error as e:
            print(f"Ошибка: {e}")
        finally:
            conn.close()
    return jsonify(results)


@profile_bp.route('/api/search-city')
def api_search_city():
    query = request.args.get('q', '').strip()
    region_id = request.args.get('region_id', type=int)
    
    if len(query) < 2:
        return jsonify([])
    
    conn = get_db_connection()
    results = []
    if conn:
        cursor = conn.cursor(dictionary=True)
        try:
            sql = """
                SELECT id, name, region_id FROM city 
                WHERE name LIKE %s
            """
            params = [f'%{query}%']
            if region_id:
                sql += " AND region_id = %s"
                params.append(region_id)
            sql += " ORDER BY name LIMIT 10"
            
            cursor.execute(sql, params)
            results = cursor.fetchall()
        except Error as e:
            print(f"Ошибка: {e}")
        finally:
            conn.close()
    return jsonify(results)


@profile_bp.route('/api/search-street')
def api_search_street():
    query = request.args.get('q', '').strip()
    city_id = request.args.get('city_id', type=int)
    
    if len(query) < 2:
        return jsonify([])
    
    conn = get_db_connection()
    results = []
    if conn:
        cursor = conn.cursor(dictionary=True)
        try:
            sql = """
                SELECT id, name, city_id FROM street 
                WHERE name LIKE %s
            """
            params = [f'%{query}%']
            if city_id:
                sql += " AND city_id = %s"
                params.append(city_id)
            sql += " ORDER BY name LIMIT 10"
            
            cursor.execute(sql, params)
            results = cursor.fetchall()
        except Error as e:
            print(f"Ошибка: {e}")
        finally:
            conn.close()
    return jsonify(results)


@profile_bp.route('/api/get-city-streets')
def api_get_city_streets():
    city_id = request.args.get('city_id', type=int)
    if not city_id:
        return jsonify([])
    
    conn = get_db_connection()
    results = []
    if conn:
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute("""
                SELECT id, name FROM street 
                WHERE city_id = %s 
                ORDER BY name LIMIT 50
            """, (city_id,))
            results = cursor.fetchall()
        except Error as e:
            print(f"Ошибка: {e}")
        finally:
            conn.close()
    return jsonify(results)


@profile_bp.route('/profile/address/add', methods=['POST'])
@login_required
def add_delivery_address():
    """Добавление адреса доставки с использованием ID из БД"""
    country_id = request.form.get('country_id', type=int)
    region_id = request.form.get('region_id', type=int)
    city_id = request.form.get('city_id', type=int)
    street_id = request.form.get('street_id', type=int)
    house = request.form.get('house', '').strip()
    apartment = request.form.get('apartment', '').strip()
    entrance = request.form.get('entrance', '')
    floor = request.form.get('floor', type=int) or None
    postal_code = request.form.get('postal_code', '').strip()
    is_default = request.form.get('is_default') == 'on'
    
    if not all([country_id, region_id, city_id, street_id, house]):
        flash('Заполните все обязательные поля', 'danger')
        return redirect(url_for('profile.profile'))
    
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        try:
            # Если адрес по умолчанию - сбрасываем остальные
            if is_default:
                cursor.execute("UPDATE address SET is_default = FALSE WHERE user_id = %s", (session['user_id'],))
            
            # Добавляем адрес
            cursor.execute("""
                INSERT INTO address (user_id, street_id, house, apartment, entrance, floor, postal_code, is_default)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (session['user_id'], street_id, house, apartment, entrance, floor, postal_code, is_default))
            conn.commit()
            
            flash('Адрес успешно добавлен!', 'success')
        except Error as e:
            conn.rollback()
            flash(f'Ошибка добавления адреса: {str(e)}', 'danger')
        finally:
            conn.close()
    
    return redirect(url_for('profile.profile'))


@profile_bp.route('/profile/address/delete/<int:address_id>')
@login_required
def delete_delivery_address(address_id):
    """Удаление адреса доставки"""
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        try:
            cursor.execute("DELETE FROM address WHERE id = %s AND user_id = %s", (address_id, session['user_id']))
            conn.commit()
            flash('Адрес удален', 'success')
        except Error as e:
            flash(f'Ошибка: {e}', 'danger')
        finally:
            conn.close()
    
    return redirect(url_for('profile.profile'))


@profile_bp.route('/profile/address/set-default/<int:address_id>')
@login_required
def set_default_address(address_id):
    """Установка адреса по умолчанию"""
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        try:
            cursor.execute("UPDATE address SET is_default = FALSE WHERE user_id = %s", (session['user_id'],))
            cursor.execute("UPDATE address SET is_default = TRUE WHERE id = %s AND user_id = %s", (address_id, session['user_id']))
            conn.commit()
            flash('Адрес установлен как основной', 'success')
        except Error as e:
            flash(f'Ошибка: {e}', 'danger')
        finally:
            conn.close()
    
    return redirect(url_for('profile.profile'))