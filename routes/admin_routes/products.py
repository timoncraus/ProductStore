from flask import Blueprint, render_template, request, redirect, url_for, flash
from decorators import admin_required
from helpers import get_db_connection
from mysql.connector import Error

products_bp = Blueprint('products', __name__)

@products_bp.route('/')
@admin_required
def products():
    conn = get_db_connection()
    products = []
    
    if conn:
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute("""
                SELECT p.*, c.name as category_name
                FROM product p
                LEFT JOIN category c ON p.category_id = c.id
                ORDER BY p.created_at DESC
            """)
            products = cursor.fetchall()
            for product in products:
                if product.get('price'):
                    product['price'] = float(product['price'])
                if product.get('old_price'):
                    product['old_price'] = float(product['old_price'])
        except Error as e:
            flash(f'Ошибка: {e}', 'danger')
        finally:
            conn.close()
    
    return render_template('admin/products.html', products=products)

@products_bp.route('/add', methods=['GET', 'POST'])
@admin_required
def products_add():
    conn = get_db_connection()
    categories = []
    
    if conn:
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute("SELECT id, name FROM category ORDER BY sort_order, name")
            categories = cursor.fetchall()
        except Error as e:
            flash(f'Ошибка: {e}', 'danger')
        finally:
            conn.close()
    
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        description = request.form.get('description', '')
        price = request.form.get('price', type=float)
        old_price = request.form.get('old_price', type=float) or None
        category_id = request.form.get('category_id', type=int)
        stock = request.form.get('stock', type=int, default=0)
        unit = request.form.get('unit', 'шт')
        is_new = request.form.get('is_new') == 'on'
        is_hit = request.form.get('is_hit') == 'on'
        image_url = request.form.get('image_url', '/static/images/products/default-product.jpg')
        image_alt = request.form.get('image_alt', name)
        
        if not name or not price or not category_id:
            flash('Заполните обязательные поля (Название, Цена, Категория)', 'danger')
        else:
            conn = get_db_connection()
            if conn:
                cursor = conn.cursor()
                try:
                    cursor.execute("""
                        INSERT INTO product (name, description, price, old_price, 
                                           category_id, stock, unit, is_new, is_hit,
                                           image_url, image_alt)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """, (name, description, price, old_price, 
                          category_id, stock, unit, is_new, is_hit,
                          image_url, image_alt))
                    conn.commit()
                    flash(f'Товар "{name}" успешно добавлен!', 'success')
                    return redirect(url_for('admin.products.products'))
                except Error as e:
                    conn.rollback()
                    flash(f'Ошибка: {str(e)}', 'danger')
                finally:
                    conn.close()
    
    return render_template('admin/product_add.html', categories=categories)

@products_bp.route('/edit/<int:product_id>', methods=['GET', 'POST'])
@admin_required
def products_edit(product_id):
    conn = get_db_connection()
    product = None
    categories = []
    
    if conn:
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute("SELECT id, name FROM category ORDER BY sort_order, name")
            categories = cursor.fetchall()
            
            if request.method == 'POST':
                name = request.form.get('name', '').strip()
                description = request.form.get('description', '')
                price = request.form.get('price', type=float)
                old_price = request.form.get('old_price', type=float) or None
                category_id = request.form.get('category_id', type=int)
                stock = request.form.get('stock', type=int, default=0)
                unit = request.form.get('unit', 'шт')
                is_active = request.form.get('is_active') == 'on'
                is_new = request.form.get('is_new') == 'on'
                is_hit = request.form.get('is_hit') == 'on'
                image_url = request.form.get('image_url', '/static/images/products/default-product.jpg')
                image_alt = request.form.get('image_alt', name)
                
                cursor.execute("""
                    UPDATE product 
                    SET name=%s, description=%s, price=%s, old_price=%s,
                        category_id=%s, stock=%s, unit=%s,
                        is_active=%s, is_new=%s, is_hit=%s,
                        image_url=%s, image_alt=%s
                    WHERE id=%s
                """, (name, description, price, old_price,
                      category_id, stock, unit,
                      is_active, is_new, is_hit,
                      image_url, image_alt, product_id))
                conn.commit()
                flash('Товар обновлён', 'success')
                return redirect(url_for('admin.products.products'))
            
            cursor.execute("SELECT * FROM product WHERE id = %s", (product_id,))
            product = cursor.fetchone()
            if product:
                product['price'] = float(product['price'])
                if product['old_price']:
                    product['old_price'] = float(product['old_price'])
            
        except Error as e:
            flash(f'Ошибка: {e}', 'danger')
        finally:
            conn.close()
    
    if not product:
        flash('Товар не найден', 'danger')
        return redirect(url_for('admin.products.products'))
    
    return render_template('admin/product_edit.html', product=product, categories=categories)

@products_bp.route('/delete/<int:product_id>')
@admin_required
def products_delete(product_id):
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT COUNT(*) FROM order_item WHERE product_id = %s", (product_id,))
            if cursor.fetchone()[0] > 0:
                flash('Нельзя удалить товар - он есть в заказах', 'danger')
            else:
                cursor.execute("DELETE FROM product WHERE id = %s", (product_id,))
                conn.commit()
                flash('Товар удалён', 'success')
        except Error as e:
            flash(f'Ошибка: {e}', 'danger')
        finally:
            conn.close()
    
    return redirect(url_for('admin.products.products'))