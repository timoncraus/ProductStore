from flask import Blueprint, render_template, request, redirect, url_for, flash
from routes.admin import admin_bp
from decorators import admin_required
from helpers import get_db_connection
from mysql.connector import Error

categories_bp = Blueprint('categories', __name__)

@categories_bp.route('/')
@admin_required
def categories():
    conn = get_db_connection()
    categories = []
    
    if conn:
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute("""
                SELECT c.*, 
                       (SELECT COUNT(*) FROM product WHERE category_id = c.id) as products_count
                FROM category c
                ORDER BY c.sort_order, c.name
            """)
            categories = cursor.fetchall()
        except Error as e:
            flash(f'Ошибка: {e}', 'danger')
        finally:
            conn.close()
    
    return render_template('admin/categories.html', categories=categories)

@categories_bp.route('/add', methods=['POST'])
@admin_required
def category_add():
    name = request.form.get('name', '').strip()
    sort_order = request.form.get('sort_order', type=int, default=0)
    is_active = request.form.get('is_active') == 'on'
    image_url = request.form.get('image_url', '/static/images/categories/default-category.jpg')
    
    if not name:
        flash('Введите название категории', 'danger')
    else:
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor()
            try:
                cursor.execute("""
                    INSERT INTO category (name, sort_order, is_active, image_url)
                    VALUES (%s, %s, %s, %s)
                """, (name, sort_order, is_active, image_url))
                conn.commit()
                flash(f'Категория "{name}" добавлена', 'success')
            except Error as e:
                flash(f'Ошибка: {e}', 'danger')
            finally:
                conn.close()
    
    return redirect(url_for('admin.admin_categories'))

@categories_bp.route('/edit/<int:category_id>', methods=['POST'])
@admin_required
def category_edit(category_id):
    name = request.form.get('name', '').strip()
    sort_order = request.form.get('sort_order', type=int, default=0)
    is_active = request.form.get('is_active') == 'on'
    image_url = request.form.get('image_url', '/static/images/categories/default-category.jpg')
    
    if not name:
        flash('Введите название категории', 'danger')
    else:
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor()
            try:
                cursor.execute("""
                    UPDATE category 
                    SET name=%s, sort_order=%s, is_active=%s, image_url=%s
                    WHERE id=%s
                """, (name, sort_order, is_active, image_url, category_id))
                conn.commit()
                flash('Категория обновлена', 'success')
            except Error as e:
                flash(f'Ошибка: {e}', 'danger')
            finally:
                conn.close()
    
    return redirect(url_for('admin.admin_categories'))

@categories_bp.route('/delete/<int:category_id>')
@admin_required
def category_delete(category_id):
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        try:
            # Проверяем, есть ли товары в этой категории
            cursor.execute("SELECT COUNT(*) as count FROM product WHERE category_id = %s", (category_id,))
            result = cursor.fetchone()
            if result and result[0] > 0:
                flash(f'Нельзя удалить категорию - в ней есть товары ({result[0]} шт.)', 'danger')
            else:
                cursor.execute("DELETE FROM category WHERE id = %s", (category_id,))
                conn.commit()
                flash('Категория удалена', 'success')
        except Error as e:
            flash(f'Ошибка: {e}', 'danger')
        finally:
            conn.close()
    
    return redirect(url_for('admin.admin_categories'))