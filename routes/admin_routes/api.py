from flask import Blueprint, request, jsonify
from routes.admin import admin_bp
from decorators import admin_required
from helpers import get_db_connection
from mysql.connector import Error

api_bp = Blueprint('api', __name__)

# API для стран
@api_bp.route('/country/add', methods=['POST'])
@admin_required
def add_country():
    name = request.json.get('name')
    code = request.json.get('code')
    
    if not name:
        return jsonify({'success': False, 'error': 'Название обязательно'})
    
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO country (name, code) VALUES (%s, %s)", (name, code))
            conn.commit()
            return jsonify({'success': True, 'id': cursor.lastrowid})
        except Error as e:
            return jsonify({'success': False, 'error': str(e)})
        finally:
            conn.close()
    return jsonify({'success': False, 'error': 'Ошибка подключения'})

@api_bp.route('/country/edit/<int:country_id>', methods=['PUT'])
@admin_required
def edit_country(country_id):
    name = request.json.get('name')
    code = request.json.get('code')
    
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        try:
            cursor.execute("UPDATE country SET name=%s, code=%s WHERE id=%s", (name, code, country_id))
            conn.commit()
            return jsonify({'success': True})
        except Error as e:
            return jsonify({'success': False, 'error': str(e)})
        finally:
            conn.close()
    return jsonify({'success': False, 'error': 'Ошибка подключения'})

@api_bp.route('/country/delete/<int:country_id>', methods=['DELETE'])
@admin_required
def delete_country(country_id):
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT COUNT(*) FROM region WHERE country_id = %s", (country_id,))
            if cursor.fetchone()[0] > 0:
                return jsonify({'success': False, 'error': 'Нельзя удалить страну - есть связанные регионы'})
            cursor.execute("DELETE FROM country WHERE id = %s", (country_id,))
            conn.commit()
            return jsonify({'success': True})
        except Error as e:
            return jsonify({'success': False, 'error': str(e)})
        finally:
            conn.close()
    return jsonify({'success': False, 'error': 'Ошибка подключения'})

# API для регионов
@api_bp.route('/region/add', methods=['POST'])
@admin_required
def add_region():
    name = request.json.get('name')
    country_id = request.json.get('country_id')
    
    if not name or not country_id:
        return jsonify({'success': False, 'error': 'Заполните все поля'})
    
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO region (name, country_id) VALUES (%s, %s)", (name, country_id))
            conn.commit()
            return jsonify({'success': True, 'id': cursor.lastrowid})
        except Error as e:
            return jsonify({'success': False, 'error': str(e)})
        finally:
            conn.close()
    return jsonify({'success': False, 'error': 'Ошибка подключения'})

# API для городов
@api_bp.route('/city/add', methods=['POST'])
@admin_required
def add_city():
    name = request.json.get('name')
    region_id = request.json.get('region_id')
    
    if not name or not region_id:
        return jsonify({'success': False, 'error': 'Заполните все поля'})
    
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO city (name, region_id) VALUES (%s, %s)", (name, region_id))
            conn.commit()
            return jsonify({'success': True, 'id': cursor.lastrowid})
        except Error as e:
            return jsonify({'success': False, 'error': str(e)})
        finally:
            conn.close()
    return jsonify({'success': False, 'error': 'Ошибка подключения'})

# API для улиц
@api_bp.route('/street/add', methods=['POST'])
@admin_required
def add_street():
    name = request.json.get('name')
    city_id = request.json.get('city_id')
    
    if not name or not city_id:
        return jsonify({'success': False, 'error': 'Заполните все поля'})
    
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO street (name, city_id) VALUES (%s, %s)", (name, city_id))
            conn.commit()
            return jsonify({'success': True, 'id': cursor.lastrowid})
        except Error as e:
            return jsonify({'success': False, 'error': str(e)})
        finally:
            conn.close()
    return jsonify({'success': False, 'error': 'Ошибка подключения'})