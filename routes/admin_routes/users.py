from flask import Blueprint, session, flash, redirect, url_for, render_template, request
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
        return redirect(url_for('admin.users.users'))
    
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        try:
            cursor.execute("UPDATE user SET is_active = NOT is_active WHERE id = %s", (user_id,))
            conn.commit()
            
            # Проверяем новый статус
            cursor.execute("SELECT is_active FROM user WHERE id = %s", (user_id,))
            result = cursor.fetchone()
            if result and result[0]:
                flash('Пользователь разблокирован', 'success')
            else:
                flash('Пользователь заблокирован', 'success')
        except Error as e:
            flash(f'Ошибка: {e}', 'danger')
        finally:
            conn.close()
    
    return redirect(url_for('admin.users.users'))

@users_bp.route('/detail/<int:user_id>')
@admin_required
def user_detail(user_id):
    conn = get_db_connection()
    user = None
    
    if conn:
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute("""
                SELECT u.*, 
                       (SELECT COUNT(*) FROM orders WHERE user_id = u.id) as orders_count,
                       (SELECT COALESCE(SUM(total_amount), 0) FROM orders WHERE user_id = u.id) as total_spent
                FROM user u
                WHERE u.id = %s
            """, (user_id,))
            user = cursor.fetchone()
            if user and user.get('total_spent'):
                user['total_spent'] = float(user['total_spent'])
        except Error as e:
            flash(f'Ошибка: {e}', 'danger')
        finally:
            conn.close()
    
    if not user:
        flash('Пользователь не найден', 'danger')
        return redirect(url_for('admin.users.users'))
    
    return render_template('admin/user_detail.html', user=user)

@users_bp.route('/delete/<int:user_id>')
@admin_required
def user_delete(user_id):
    if user_id == session.get('user_id'):
        flash('Нельзя удалить самого себя', 'danger')
        return redirect(url_for('admin.users.users'))
    
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        try:
            # Проверяем, есть ли заказы у пользователя
            cursor.execute("SELECT COUNT(*) as count FROM orders WHERE user_id = %s", (user_id,))
            result = cursor.fetchone()
            if result and result[0] > 0:
                flash(f'Нельзя удалить пользователя - у него есть заказы ({result[0]} шт.)', 'danger')
            else:
                cursor.execute("DELETE FROM user WHERE id = %s", (user_id,))
                conn.commit()
                flash('Пользователь удален', 'success')
        except Error as e:
            flash(f'Ошибка: {e}', 'danger')
        finally:
            conn.close()
    
    return redirect(url_for('admin.users.users'))