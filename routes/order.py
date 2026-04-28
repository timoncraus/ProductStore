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
                return redirect(url_for('catalog.catalog'))
            
            if request.method == 'POST':
                delivery_address = request.form.get('delivery_address', '')
                recipient_name = request.form.get('recipient_name', '')
                recipient_phone = request.form.get('recipient_phone', '')
                comment = request.form.get('comment', '')
                
                if not delivery_address:
                    flash('Введите адрес доставки', 'danger')
                    return redirect(url_for('checkout.checkout'))
                
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
                return redirect(url_for('profile.profile'))
                
        except Error as e:
            conn.rollback()
            flash(f'Ошибка оформления заказа: {str(e)}', 'danger')
        finally:
            conn.close()
    
    return render_template('user/checkout.html', 
                          cart_items=cart_items, 
                          total=total,
                          user=user)