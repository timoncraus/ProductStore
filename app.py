from flask import Flask, render_template
import secrets
from datetime import timedelta
import sys, os

app = Flask(__name__)
app.secret_key = secrets.token_hex(32)
app.permanent_session_lifetime = timedelta(hours=24)

@app.context_processor
def utility_processor():
    def url_for(endpoint, **values):
        try:
            from flask import url_for
            return url_for(endpoint, **values)
        except Exception as e:
            print(f"URL Error: {endpoint} - {e}")
            return "#"
    return dict(url_for=url_for)

from routes import main_bp, catalog_bp, cart_bp, profile_bp, order_bp, admin_bp

app.register_blueprint(main_bp)
app.register_blueprint(profile_bp)
app.register_blueprint(catalog_bp, url_prefix='/catalog')
app.register_blueprint(cart_bp, url_prefix='/cart')
app.register_blueprint(order_bp, url_prefix='/order')
app.register_blueprint(admin_bp, url_prefix='/admin')

@app.errorhandler(404)
def page_not_found(error):
    """Страница 404 - не найдено"""
    return render_template('404.html'), 404

@app.errorhandler(403)
def forbidden(error):
    """Страница 403 - доступ запрещен"""
    return render_template('403.html'), 403

@app.errorhandler(500)
def internal_server_error(error):
    """Страница 500 - внутренняя ошибка сервера"""
    return render_template('500.html'), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)