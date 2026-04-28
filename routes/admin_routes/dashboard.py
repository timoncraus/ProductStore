from flask import Blueprint, render_template, session, flash, redirect, url_for
from routes.admin import admin_bp
from decorators import admin_required
from helpers import get_db_connection
from mysql.connector import Error

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/')
@admin_required
def dashboard():
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
            stats['revenue_today'] = float(today['total']) if today and today['total'] else 0
            
            cursor.execute("""
                SELECT COUNT(*) as count, COALESCE(SUM(total_amount), 0) as total
                FROM orders WHERE status_id NOT IN (6)
            """)
            total_data = cursor.fetchone()
            stats['orders_total'] = total_data['count'] if total_data else 0
            stats['revenue_total'] = float(total_data['total']) if total_data and total_data['total'] else 0
            
            cursor.execute("SELECT COUNT(*) as count FROM user WHERE DATE(created_at) = CURDATE()")
            stats['new_users_today'] = cursor.fetchone()['count']
            
            cursor.execute("SELECT COUNT(*) as count FROM product WHERE stock <= 10 AND stock > 0")
            stats['low_stock_products'] = cursor.fetchone()['count']
            
            cursor.execute("""
                SELECT o.*, u.username, u.email, os.name as status_name
                FROM orders o
                JOIN user u ON o.user_id = u.id
                JOIN order_status os ON o.status_id = os.id
                ORDER BY o.created_at DESC
                LIMIT 10
            """)
            recent_orders = cursor.fetchall()
            for order in recent_orders:
                if order.get('total_amount'):
                    order['total_amount'] = float(order['total_amount'])
            
            cursor.execute("""
                SELECT id, username, email, first_name, last_name, created_at
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