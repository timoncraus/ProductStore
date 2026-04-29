from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from helpers import *
from decorators import *

order_bp = Blueprint('order', __name__)

@order_bp.route('/checkout', methods=['GET', 'POST'])
@login_required
def checkout():
    """Оформление заказа"""
    conn = get_db_connection()
    cart_items = []
    total = 0
    user = None
    addresses = []
    
    if conn:
        cursor = conn.cursor(dictionary=True)
        try:
            # Получаем данные пользователя
            cursor.execute("""
                SELECT id, username, first_name, last_name, email, phone 
                FROM user WHERE id = %s
            """, (session['user_id'],))
            user = cursor.fetchone()
            
            # Получаем адреса пользователя
            cursor.execute("""
                SELECT a.*, s.name as street_name, c.name as city_name, 
                       r.name as region_name, co.name as country_name
                FROM address a
                JOIN street s ON a.street_id = s.id
                JOIN city c ON s.city_id = c.id
                JOIN region r ON c.region_id = r.id
                JOIN country co ON r.country_id = co.id
                WHERE a.user_id = %s
                ORDER BY a.is_default DESC, a.created_at DESC
            """, (session['user_id'],))
            addresses = cursor.fetchall()
            
            # Получаем товары в корзине
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
                return redirect(url_for('catalog.catalog'))
            
            if request.method == 'POST':
                address_id = request.form.get('address_id', type=int)
                comment = request.form.get('comment', '')
                
                # Проверяем, что выбран существующий адрес
                if not address_id or address_id <= 0:
                    flash('Пожалуйста, выберите адрес доставки', 'danger')
                    return redirect(url_for('order.checkout'))
                
                # Проверяем, что адрес принадлежит пользователю
                cursor.execute("""
                    SELECT id FROM address WHERE id = %s AND user_id = %s
                """, (address_id, session['user_id']))
                if not cursor.fetchone():
                    flash('Выбран неверный адрес', 'danger')
                    return redirect(url_for('order.checkout'))
                
                # Создаем заказ
                order_number = generate_order_number()
                
                cursor.execute("""
                    INSERT INTO orders (user_id, order_number, total_amount, address_id, comment)
                    VALUES (%s, %s, %s, %s, %s)
                """, (session['user_id'], order_number, total, address_id, comment))
                
                order_id = cursor.lastrowid
                
                # Добавляем товары в заказ
                for item in cart_items:
                    cursor.execute("""
                        INSERT INTO order_item (order_id, product_id, product_name, quantity, price)
                        VALUES (%s, %s, %s, %s, %s)
                    """, (order_id, item['product_id'], item['name'], 
                          item['quantity'], item['price']))
                    
                    # Обновляем остатки и продажи
                    cursor.execute("""
                        UPDATE product 
                        SET stock = stock - %s, sales_count = sales_count + %s
                        WHERE id = %s
                    """, (item['quantity'], item['quantity'], item['product_id']))
                
                # Очищаем корзину
                cursor.execute("""
                    DELETE FROM cart_item WHERE cart_id = (
                        SELECT id FROM cart WHERE user_id = %s
                    )
                """, (session['user_id'],))
                
                conn.commit()
                flash(f'Заказ #{order_number} успешно оформлен!', 'success')
                return redirect(url_for('profile.profile', tab='orders'))
                
        except Error as e:
            conn.rollback()
            flash(f'Ошибка оформления заказа: {str(e)}', 'danger')
        finally:
            conn.close()
    
    return render_template('user/checkout.html', 
                          cart_items=cart_items, 
                          total=total,
                          user=user,
                          addresses=addresses)


# API для автодополнения адресов (для checkout)
@order_bp.route('/api/search-country')
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


@order_bp.route('/api/search-region')
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


@order_bp.route('/api/search-city')
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


@order_bp.route('/api/search-street')
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