from flask import Blueprint, render_template, request, redirect, url_for, flash
from routes.admin import admin_bp
from decorators import admin_required
from helpers import get_db_connection
from mysql.connector import Error

orders_bp = Blueprint('orders', __name__)

@orders_bp.route('/')
@admin_required
def orders():
    conn = get_db_connection()
    orders = []
    statuses = []
    
    if conn:
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute("""
                SELECT o.*, u.username, u.email, u.phone, os.name as status_name,
                       CONCAT(c.name, ', ', r.name, ', ', ct.name, ', ул. ', s.name, ', д. ', a.house,
                              IF(a.apartment IS NOT NULL AND a.apartment != '', CONCAT(', кв. ', a.apartment), '')) as full_address
                FROM orders o
                JOIN user u ON o.user_id = u.id
                JOIN order_status os ON o.status_id = os.id
                JOIN address a ON o.address_id = a.id
                JOIN street s ON a.street_id = s.id
                JOIN city ct ON s.city_id = ct.id
                JOIN region r ON ct.region_id = r.id
                JOIN country c ON r.country_id = c.id
                ORDER BY o.created_at DESC
            """)
            orders = cursor.fetchall()
            for order in orders:
                if order.get('total_amount'):
                    order['total_amount'] = float(order['total_amount'])
            
            cursor.execute("SELECT * FROM order_status ORDER BY id")
            statuses = cursor.fetchall()
        except Error as e:
            flash(f'Ошибка: {e}', 'danger')
        finally:
            conn.close()
    
    return render_template('admin/orders.html', orders=orders, statuses=statuses)

@orders_bp.route('/<int:order_id>')
@admin_required
def order_detail(order_id):
    conn = get_db_connection()
    order = None
    items = []
    statuses = []
    
    if conn:
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute("""
                SELECT o.*, u.username, u.email, u.phone, u.first_name, u.last_name,
                       os.name as status_name,
                       CONCAT(c.name, ', ', r.name, ', ', ct.name, ', ул. ', s.name, ', д. ', a.house,
                              IF(a.apartment IS NOT NULL AND a.apartment != '', CONCAT(', кв. ', a.apartment), '')) as full_address,
                       a.postal_code, a.entrance, a.floor
                FROM orders o
                JOIN user u ON o.user_id = u.id
                JOIN order_status os ON o.status_id = os.id
                JOIN address a ON o.address_id = a.id
                JOIN street s ON a.street_id = s.id
                JOIN city ct ON s.city_id = ct.id
                JOIN region r ON ct.region_id = r.id
                JOIN country c ON r.country_id = c.id
                WHERE o.id = %s
            """, (order_id,))
            order = cursor.fetchone()
            if order:
                order['total_amount'] = float(order['total_amount'])
            
            cursor.execute("""
                SELECT oi.*, p.image_url, p.unit
                FROM order_item oi
                JOIN product p ON oi.product_id = p.id
                WHERE oi.order_id = %s
            """, (order_id,))
            items = cursor.fetchall()
            for item in items:
                if item.get('price'):
                    item['price'] = float(item['price'])
            
            cursor.execute("SELECT * FROM order_status ORDER BY id")
            statuses = cursor.fetchall()
        except Error as e:
            flash(f'Ошибка: {e}', 'danger')
        finally:
            conn.close()
    
    if not order:
        flash('Заказ не найден', 'danger')
        return redirect(url_for('admin.admin_orders'))
    
    return render_template('admin/order_detail.html', order=order, items=items, statuses=statuses)

@orders_bp.route('/<int:order_id>/status', methods=['POST'])
@admin_required
def order_update_status(order_id):
    status_id = request.form.get('status_id', type=int)
    
    if not status_id:
        flash('Выберите статус', 'danger')
        return redirect(url_for('admin.admin_orders'))
    
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
    
    # Если запрос пришел с детальной страницы, возвращаемся туда
    referer = request.referrer
    if referer and f'/admin/orders/{order_id}' in referer:
        return redirect(url_for('admin.admin_order_detail', order_id=order_id))
    return redirect(url_for('admin.admin_orders'))