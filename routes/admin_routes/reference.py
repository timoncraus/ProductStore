from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from decorators import admin_required
from helpers import get_db_connection
from mysql.connector import Error

reference_bp = Blueprint('reference', __name__)

# =====================================================
# СТРАНЫ
# =====================================================
@reference_bp.route('/countries')
@admin_required
def countries():
    conn = get_db_connection()
    countries = []
    
    if conn:
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute("""
                SELECT c.*, COUNT(r.id) as regions_count
                FROM country c
                LEFT JOIN region r ON c.id = r.country_id
                GROUP BY c.id
                ORDER BY c.name
            """)
            countries = cursor.fetchall()
        except Error as e:
            flash(f'Ошибка: {e}', 'danger')
        finally:
            conn.close()
    
    return render_template('admin/countries.html', countries=countries)

@reference_bp.route('/countries/add', methods=['POST'])
@admin_required
def country_add():
    name = request.form.get('name', '').strip()
    code = request.form.get('code', '').strip()
    
    if not name:
        flash('Введите название страны', 'danger')
    else:
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor()
            try:
                cursor.execute("INSERT INTO country (name, code) VALUES (%s, %s)", (name, code))
                conn.commit()
                flash(f'Страна "{name}" добавлена', 'success')
            except Error as e:
                flash(f'Ошибка: {e}', 'danger')
            finally:
                conn.close()
    
    return redirect(url_for('admin.reference.countries'))

@reference_bp.route('/countries/edit/<int:country_id>', methods=['POST'])
@admin_required
def country_edit(country_id):
    name = request.form.get('name', '').strip()
    code = request.form.get('code', '').strip()
    
    if not name:
        flash('Введите название страны', 'danger')
    else:
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor()
            try:
                cursor.execute("UPDATE country SET name=%s, code=%s WHERE id=%s", (name, code, country_id))
                conn.commit()
                flash('Страна обновлена', 'success')
            except Error as e:
                flash(f'Ошибка: {e}', 'danger')
            finally:
                conn.close()
    
    return redirect(url_for('admin.reference.countries'))

@reference_bp.route('/countries/delete/<int:country_id>')
@admin_required
def country_delete(country_id):
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT COUNT(*) FROM region WHERE country_id = %s", (country_id,))
            if cursor.fetchone()[0] > 0:
                flash('Нельзя удалить страну - есть связанные регионы', 'danger')
            else:
                cursor.execute("DELETE FROM country WHERE id = %s", (country_id,))
                conn.commit()
                flash('Страна удалена', 'success')
        except Error as e:
            flash(f'Ошибка: {e}', 'danger')
        finally:
            conn.close()
    
    return redirect(url_for('admin.reference.countries'))

# =====================================================
# РЕГИОНЫ
# =====================================================
@reference_bp.route('/regions')
@admin_required
def regions():
    conn = get_db_connection()
    regions = []
    countries = []
    
    if conn:
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute("""
                SELECT r.*, c.name as country_name, c.id as country_id, COUNT(ct.id) as cities_count
                FROM region r
                JOIN country c ON r.country_id = c.id
                LEFT JOIN city ct ON r.id = ct.region_id
                GROUP BY r.id
                ORDER BY c.name, r.name
            """)
            regions = cursor.fetchall()
            
            cursor.execute("SELECT id, name FROM country ORDER BY name")
            countries = cursor.fetchall()
        except Error as e:
            flash(f'Ошибка: {e}', 'danger')
        finally:
            conn.close()
    
    return render_template('admin/regions.html', regions=regions, countries=countries)

@reference_bp.route('/regions/add', methods=['POST'])
@admin_required
def region_add():
    name = request.form.get('name', '').strip()
    country_id = request.form.get('country_id', type=int)
    
    if not name or not country_id:
        flash('Заполните все поля', 'danger')
    else:
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor()
            try:
                cursor.execute("INSERT INTO region (name, country_id) VALUES (%s, %s)", (name, country_id))
                conn.commit()
                flash(f'Регион "{name}" добавлен', 'success')
            except Error as e:
                flash(f'Ошибка: {e}', 'danger')
            finally:
                conn.close()
    
    return redirect(url_for('admin.reference.regions'))

@reference_bp.route('/regions/edit/<int:region_id>', methods=['POST'])
@admin_required
def region_edit(region_id):
    name = request.form.get('name', '').strip()
    country_id = request.form.get('country_id', type=int)
    
    if not name or not country_id:
        flash('Заполните все поля', 'danger')
    else:
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor()
            try:
                cursor.execute("UPDATE region SET name=%s, country_id=%s WHERE id=%s", (name, country_id, region_id))
                conn.commit()
                flash('Регион обновлен', 'success')
            except Error as e:
                flash(f'Ошибка: {e}', 'danger')
            finally:
                conn.close()
    
    return redirect(url_for('admin.reference.regions'))

@reference_bp.route('/regions/delete/<int:region_id>')
@admin_required
def region_delete(region_id):
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT COUNT(*) FROM city WHERE region_id = %s", (region_id,))
            if cursor.fetchone()[0] > 0:
                flash('Нельзя удалить регион - есть связанные города', 'danger')
            else:
                cursor.execute("DELETE FROM region WHERE id = %s", (region_id,))
                conn.commit()
                flash('Регион удален', 'success')
        except Error as e:
            flash(f'Ошибка: {e}', 'danger')
        finally:
            conn.close()
    
    return redirect(url_for('admin.reference.regions'))

# =====================================================
# ГОРОДА
# =====================================================
@reference_bp.route('/cities')
@admin_required
def cities():
    conn = get_db_connection()
    cities = []
    regions = []
    
    if conn:
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute("""
                SELECT ct.*, r.name as region_name, r.id as region_id, c.name as country_name, COUNT(s.id) as streets_count
                FROM city ct
                JOIN region r ON ct.region_id = r.id
                JOIN country c ON r.country_id = c.id
                LEFT JOIN street s ON ct.id = s.city_id
                GROUP BY ct.id
                ORDER BY c.name, r.name, ct.name
            """)
            cities = cursor.fetchall()
            
            cursor.execute("""
                SELECT r.id, r.name, c.name as country_name
                FROM region r
                JOIN country c ON r.country_id = c.id
                ORDER BY c.name, r.name
            """)
            regions = cursor.fetchall()
        except Error as e:
            flash(f'Ошибка: {e}', 'danger')
        finally:
            conn.close()
    
    return render_template('admin/cities.html', cities=cities, regions=regions)

@reference_bp.route('/cities/add', methods=['POST'])
@admin_required
def city_add():
    name = request.form.get('name', '').strip()
    region_id = request.form.get('region_id', type=int)
    
    if not name or not region_id:
        flash('Заполните все поля', 'danger')
    else:
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor()
            try:
                cursor.execute("INSERT INTO city (name, region_id) VALUES (%s, %s)", (name, region_id))
                conn.commit()
                flash(f'Город "{name}" добавлен', 'success')
            except Error as e:
                flash(f'Ошибка: {e}', 'danger')
            finally:
                conn.close()
    
    return redirect(url_for('admin.reference.cities'))

@reference_bp.route('/cities/edit/<int:city_id>', methods=['POST'])
@admin_required
def city_edit(city_id):
    name = request.form.get('name', '').strip()
    region_id = request.form.get('region_id', type=int)
    
    if not name or not region_id:
        flash('Заполните все поля', 'danger')
    else:
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor()
            try:
                cursor.execute("UPDATE city SET name=%s, region_id=%s WHERE id=%s", (name, region_id, city_id))
                conn.commit()
                flash('Город обновлен', 'success')
            except Error as e:
                flash(f'Ошибка: {e}', 'danger')
            finally:
                conn.close()
    
    return redirect(url_for('admin.reference.cities'))

@reference_bp.route('/cities/delete/<int:city_id>')
@admin_required
def city_delete(city_id):
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT COUNT(*) FROM street WHERE city_id = %s", (city_id,))
            if cursor.fetchone()[0] > 0:
                flash('Нельзя удалить город - есть связанные улицы', 'danger')
            else:
                cursor.execute("DELETE FROM city WHERE id = %s", (city_id,))
                conn.commit()
                flash('Город удален', 'success')
        except Error as e:
            flash(f'Ошибка: {e}', 'danger')
        finally:
            conn.close()
    
    return redirect(url_for('admin.reference.cities'))

# =====================================================
# УЛИЦЫ
# =====================================================
@reference_bp.route('/streets')
@admin_required
def streets():
    conn = get_db_connection()
    streets = []
    cities = []
    
    if conn:
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute("""
                SELECT s.*, 
                       ct.id as city_id,
                       ct.name as city_name, 
                       r.name as region_name, 
                       c.name as country_name,
                       COUNT(a.id) as addresses_count
                FROM street s
                JOIN city ct ON s.city_id = ct.id
                JOIN region r ON ct.region_id = r.id
                JOIN country c ON r.country_id = c.id
                LEFT JOIN address a ON s.id = a.street_id
                GROUP BY s.id
                ORDER BY c.name, r.name, ct.name, s.name
            """)
            streets = cursor.fetchall()
            
            cursor.execute("""
                SELECT ct.id, ct.name, r.name as region_name, c.name as country_name
                FROM city ct
                JOIN region r ON ct.region_id = r.id
                JOIN country c ON r.country_id = c.id
                ORDER BY c.name, r.name, ct.name
            """)
            cities = cursor.fetchall()
        except Error as e:
            flash(f'Ошибка: {e}', 'danger')
        finally:
            conn.close()
    
    return render_template('admin/streets.html', streets=streets, cities=cities)

@reference_bp.route('/streets/add', methods=['POST'])
@admin_required
def street_add():
    name = request.form.get('name', '').strip()
    city_id = request.form.get('city_id', type=int)
    
    if not name or not city_id:
        flash('Заполните все поля', 'danger')
    else:
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor()
            try:
                cursor.execute("INSERT INTO street (name, city_id) VALUES (%s, %s)", (name, city_id))
                conn.commit()
                flash(f'Улица "{name}" добавлена', 'success')
            except Error as e:
                flash(f'Ошибка: {e}', 'danger')
            finally:
                conn.close()
    
    return redirect(url_for('admin.reference.streets'))

@reference_bp.route('/streets/edit/<int:street_id>', methods=['POST'])
@admin_required
def street_edit(street_id):
    name = request.form.get('name', '').strip()
    city_id = request.form.get('city_id', type=int)
    
    if not name or not city_id:
        flash('Заполните все поля', 'danger')
    else:
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor()
            try:
                cursor.execute("UPDATE street SET name=%s, city_id=%s WHERE id=%s", (name, city_id, street_id))
                conn.commit()
                flash('Улица обновлена', 'success')
            except Error as e:
                flash(f'Ошибка: {e}', 'danger')
            finally:
                conn.close()
    
    return redirect(url_for('admin.reference.streets'))

@reference_bp.route('/streets/delete/<int:street_id>')
@admin_required
def street_delete(street_id):
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT COUNT(*) FROM address WHERE street_id = %s", (street_id,))
            if cursor.fetchone()[0] > 0:
                flash('Нельзя удалить улицу - есть связанные адреса', 'danger')
            else:
                cursor.execute("DELETE FROM street WHERE id = %s", (street_id,))
                conn.commit()
                flash('Улица удалена', 'success')
        except Error as e:
            flash(f'Ошибка: {e}', 'danger')
        finally:
            conn.close()
    
    return redirect(url_for('admin.reference.streets'))

# API для получения регионов по стране (для AJAX)
@reference_bp.route('/api/regions/<int:country_id>')
@admin_required
def api_regions(country_id):
    conn = get_db_connection()
    regions = []
    
    if conn:
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute("SELECT id, name FROM region WHERE country_id = %s ORDER BY name", (country_id,))
            regions = cursor.fetchall()
        except Error as e:
            return jsonify({'error': str(e)}), 500
        finally:
            conn.close()
    
    return jsonify(regions)

# API для получения городов по региону (для AJAX)
@reference_bp.route('/api/cities/<int:region_id>')
@admin_required
def api_cities(region_id):
    conn = get_db_connection()
    cities = []
    
    if conn:
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute("SELECT id, name FROM city WHERE region_id = %s ORDER BY name", (region_id,))
            cities = cursor.fetchall()
        except Error as e:
            return jsonify({'error': str(e)}), 500
        finally:
            conn.close()
    
    return jsonify(cities)