from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from helpers import *

catalog_bp = Blueprint('catalog', __name__)

@catalog_bp.route('/')
def catalog():
    """Страница каталога"""
    category_id = request.args.get('category', type=int)
    page = request.args.get('page', 1, type=int)
    per_page = 24
    offset = (page - 1) * per_page
    
    conn = get_db_connection()
    products = []
    total = 0
    categories = []
    current_category = None
    
    if conn:
        cursor = conn.cursor(dictionary=True)
        
        query = """
            SELECT p.*, c.name as category_name, u.short_name as unit_name
            FROM product p
            JOIN category c ON p.category_id = c.id
            JOIN unit u ON p.unit_id = u.id
            WHERE p.is_active = TRUE
        """
        count_query = "SELECT COUNT(*) as total FROM product p WHERE p.is_active = TRUE"
        params = []
        
        if category_id:
            query += " AND p.category_id = %s"
            count_query += " AND category_id = %s"
            params.append(category_id)
            
            cursor.execute("SELECT * FROM category WHERE id = %s", (category_id,))
            current_category = cursor.fetchone()
        
        query += " ORDER BY p.sales_count DESC, p.created_at DESC LIMIT %s OFFSET %s"
        params.extend([per_page, offset])
        
        try:
            cursor.execute(query, params)
            products = cursor.fetchall()
            
            count_params = params[:-2] if params else []
            cursor.execute(count_query, count_params)
            total_row = cursor.fetchone()
            total = total_row['total'] if total_row else 0
            
            cursor.execute("""
                SELECT c.id, c.name, c.image_url,
                    (SELECT COUNT(*) FROM product WHERE category_id = c.id AND is_active = TRUE) as product_count
                FROM category c
                WHERE c.is_active = TRUE
                ORDER BY c.sort_order, c.name
            """)
            categories = cursor.fetchall()
            
        except Error as e:
            print(f"Ошибка: {e}")
            flash(f'Ошибка загрузки каталога: {e}', 'danger')
        finally:
            conn.close()
    
    total_pages = (total + per_page - 1) // per_page if total > 0 else 1
    
    return render_template('user/catalog.html', 
                          products=products, 
                          categories=categories,
                          current_category=current_category,
                          total=total,
                          page=page,
                          total_pages=total_pages,
                          category_id=category_id)

@catalog_bp.route('/search')
def search_page():
    """Отдельная страница поиска"""
    query = request.args.get('q', '').strip()
    page = request.args.get('page', 1, type=int)
    per_page = 8
    offset = (page - 1) * per_page
    
    products = []
    total = 0
    
    if query:
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor(dictionary=True)
            try:
                search_param = f"%{query}%"
                
                # ДЛЯ ОТЛАДКИ: выведем сам запрос и параметры
                print(f"Поисковый запрос: {query}")
                print(f"Параметр LIKE: {search_param}")
                
                # Проверим, что реально находится в БД
                cursor.execute("""
                    SELECT p.name, p.description, p.id
                    FROM product p
                    WHERE p.is_active = TRUE
                    LIMIT 10
                """)
                sample_products = cursor.fetchall()
                print("Примеры продуктов в БД:")
                for prod in sample_products:
                    print(f"  ID: {prod['id']}, Name: {prod['name']}, Desc: {prod['description'][:50] if prod['description'] else 'None'}")
                
                cursor.execute("""
                    SELECT p.*, c.name as category_name, u.short_name as unit_name
                    FROM product p
                    JOIN category c ON p.category_id = c.id
                    JOIN unit u ON p.unit_id = u.id
                    WHERE p.is_active = TRUE 
                    AND (p.name LIKE %s OR p.description LIKE %s)
                    ORDER BY p.sales_count DESC, p.created_at DESC
                    LIMIT %s OFFSET %s
                """, (search_param, search_param, per_page, offset))
                products = cursor.fetchall()
                
                # ДЛЯ ОТЛАДКИ: выведем реальный SQL запрос с данными
                print(f"Найдено продуктов: {len(products)}")
                for prod in products:
                    print(f"  Найден: {prod['name']}, содержит '1'? {'1' in str(prod['name']) or '1' in str(prod['description'])}")
                
                cursor.execute("""
                    SELECT COUNT(*) as total
                    FROM product p
                    WHERE p.is_active = TRUE 
                    AND (p.name LIKE %s OR p.description LIKE %s)
                """, (search_param, search_param))
                total_row = cursor.fetchone()
                total = total_row['total'] if total_row else 0
            except Error as e:
                print(f"Ошибка поиска: {e}")
                flash(f'Ошибка поиска: {e}', 'danger')
            finally:
                conn.close()
    
    total_pages = (total + per_page - 1) // per_page if total > 0 else 1
    
    return render_template('user/search.html', 
                          products=products,
                          query=query,
                          total=total,
                          page=page,
                          total_pages=total_pages)

@catalog_bp.route('/product/<int:product_id>')
def product_detail(product_id):
    """Детальная страница товара"""
    conn = get_db_connection()
    product = None
    
    if conn:
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute("""
                SELECT p.*, c.name as category_name, u.name as unit_name, u.short_name as unit_short
                FROM product p
                JOIN category c ON p.category_id = c.id
                JOIN unit u ON p.unit_id = u.id
                WHERE p.id = %s AND p.is_active = TRUE
            """, (product_id,))
            product = cursor.fetchone()
            
            # Удален блок с проверкой wishlist, так как таблицы больше нет
            
        except Error as e:
            print(f"Ошибка: {e}")
            flash(f'Ошибка загрузки товара: {e}', 'danger')
        finally:
            conn.close()
    
    if not product:
        flash('Товар не найден', 'danger')
        return redirect(url_for('catalog.catalog'))
    
    return render_template('user/product_detail.html', 
                          product=product, 
                          in_wishlist=False)