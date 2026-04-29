from flask import Blueprint, render_template, request, redirect, url_for, flash
from decorators import admin_required
from helpers import get_db_connection
from mysql.connector import Error

units_bp = Blueprint('units', __name__)

@units_bp.route('/')
@admin_required
def units():
    conn = get_db_connection()
    units = []
    
    if conn:
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute("""
                SELECT u.*, 
                       (SELECT COUNT(*) FROM product WHERE unit_id = u.id) as products_count
                FROM unit u
                ORDER BY u.sort_order, u.name
            """)
            units = cursor.fetchall()
        except Error as e:
            flash(f'Ошибка: {e}', 'danger')
        finally:
            conn.close()
    
    return render_template('admin/units.html', units=units)

@units_bp.route('/add', methods=['POST'])
@admin_required
def unit_add():
    name = request.form.get('name', '').strip()
    short_name = request.form.get('short_name', '').strip()
    sort_order = request.form.get('sort_order', type=int, default=0)
    
    if not name or not short_name:
        flash('Заполните название и краткое название единицы измерения', 'danger')
    else:
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor()
            try:
                cursor.execute("""
                    INSERT INTO unit (name, short_name, sort_order)
                    VALUES (%s, %s, %s)
                """, (name, short_name, sort_order))
                conn.commit()
                flash(f'Единица измерения "{name}" добавлена', 'success')
            except Error as e:
                if e.errno == 1062:  # Duplicate entry
                    flash(f'Единица измерения "{name}" уже существует', 'danger')
                else:
                    flash(f'Ошибка: {e}', 'danger')
            finally:
                conn.close()
    
    return redirect(url_for('admin.units.units'))

@units_bp.route('/edit/<int:unit_id>', methods=['POST'])
@admin_required
def unit_edit(unit_id):
    name = request.form.get('name', '').strip()
    short_name = request.form.get('short_name', '').strip()
    sort_order = request.form.get('sort_order', type=int, default=0)
    
    if not name or not short_name:
        flash('Заполните название и краткое название единицы измерения', 'danger')
    else:
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor()
            try:
                cursor.execute("""
                    UPDATE unit 
                    SET name=%s, short_name=%s, sort_order=%s
                    WHERE id=%s
                """, (name, short_name, sort_order, unit_id))
                conn.commit()
                flash('Единица измерения обновлена', 'success')
            except Error as e:
                if e.errno == 1062:  # Duplicate entry
                    flash(f'Единица измерения "{name}" уже существует', 'danger')
                else:
                    flash(f'Ошибка: {e}', 'danger')
            finally:
                conn.close()
    
    return redirect(url_for('admin.units.units'))

@units_bp.route('/delete/<int:unit_id>')
@admin_required
def unit_delete(unit_id):
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        try:
            # Проверяем, есть ли товары с этой единицей измерения
            cursor.execute("SELECT COUNT(*) as count FROM product WHERE unit_id = %s", (unit_id,))
            result = cursor.fetchone()
            if result and result[0] > 0:
                flash(f'Нельзя удалить единицу измерения - она используется в {result[0]} товарах', 'danger')
            else:
                cursor.execute("DELETE FROM unit WHERE id = %s", (unit_id,))
                conn.commit()
                flash('Единица измерения удалена', 'success')
        except Error as e:
            flash(f'Ошибка: {e}', 'danger')
        finally:
            conn.close()
    
    return redirect(url_for('admin.units.units'))