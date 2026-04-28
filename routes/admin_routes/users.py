from flask import Blueprint, render_template, session, flash, redirect, url_for
from routes.admin import admin_bp
from decorators import admin_required
from helpers import get_db_connection
from mysql.connector import Error

users_bp = Blueprint('users', __name__)

@users_bp.route('/')
@admin_required
def users():
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
            for user in users:
                if user.get('total_spent'):
                    user['total_spent'] = float(user['total_spent'])
        except Error as e:
            flash(f'Ошибка: {e}', 'danger')
        finally:
            conn.close()
    
    return render_template('admin/users.html', users=users)

@users_bp.route('/toggle/<int:user_id>')
@admin_required
def user_toggle(user_id):
    if user_id == session.get('user_id'):
        flash('Нельзя заблокировать самого себя', 'danger')
        return redirect(url_for('admin.admin_users'))
    
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
    
    return redirect(url_for('admin.admin_users'))