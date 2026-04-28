from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from helpers import *
from decorators import *

cart_bp = Blueprint('cart', __name__)

@cart_bp.route('/')
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

@cart_bp.route('/add', methods=['POST'])
@login_required
def add_to_cart():
    """Добавление товара в корзину"""
    product_id = request.form.get('product_id', type=int)
    quantity = request.form.get('quantity', 1, type=int)
    
    if not product_id:
        flash('Товар не найден', 'warning')
        return redirect(request.referrer or url_for('catalog.catalog'))
    
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
    
    return redirect(url_for('cart.view_cart'))

@cart_bp.route('/update', methods=['POST'])
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
    
    return redirect(url_for('cart.view_cart'))

@cart_bp.route('/update-all', methods=['POST'])
@login_required
def update_all_cart():
    """Обновление количества всех товаров в корзине"""
    conn = get_db_connection()
    if not conn:
        flash('Ошибка подключения к базе данных', 'danger')
        return redirect(url_for('cart.view_cart'))
    
    cursor = conn.cursor(dictionary=True)
    updated_count = 0
    
    try:
        # Получаем все переданные поля из формы
        for key, value in request.form.items():
            if key.startswith('quantity_') and value.isdigit():
                # Извлекаем ID товара из имени поля (quantity_123)
                cart_item_id = int(key.split('_')[1])
                new_quantity = int(value)
                
                if new_quantity < 1:
                    new_quantity = 1
                
                # Получаем информацию о товаре в корзине
                cursor.execute("""
                    SELECT ci.id, ci.product_id, ci.quantity, p.stock, p.name
                    FROM cart_item ci
                    JOIN product p ON ci.product_id = p.id
                    WHERE ci.id = %s
                """, (cart_item_id,))
                
                cart_item = cursor.fetchone()
                
                if cart_item:
                    # Проверяем наличие на складе
                    if new_quantity <= cart_item['stock']:
                        cursor.execute("""
                            UPDATE cart_item 
                            SET quantity = %s 
                            WHERE id = %s
                        """, (new_quantity, cart_item_id))
                        updated_count += 1
                    else:
                        flash(f'Недостаточно товара "{cart_item["name"]}" на складе (доступно: {cart_item["stock"]})', 'warning')
        
        conn.commit()
        
        if updated_count > 0:
            flash(f'Корзина обновлена ({updated_count} товаров)', 'success')
        else:
            flash('Ни один товар не был обновлен', 'info')
            
    except Exception as e:
        conn.rollback()
        flash(f'Ошибка при обновлении корзины: {str(e)}', 'danger')
    finally:
        conn.close()
    
    return redirect(url_for('cart.view_cart'))

@cart_bp.route('/remove/<int:item_id>')
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
    
    return redirect(url_for('cart.view_cart'))