from flask import Blueprint

admin_bp = Blueprint('admin', __name__)

from routes.admin_routes import dashboard_bp, products_bp, categories_bp, orders_bp, users_bp, reference_bp, api_bp, units_bp

admin_bp.register_blueprint(dashboard_bp)
admin_bp.register_blueprint(products_bp, url_prefix='/products')
admin_bp.register_blueprint(categories_bp, url_prefix='/categories')
admin_bp.register_blueprint(orders_bp, url_prefix='/orders')
admin_bp.register_blueprint(users_bp, url_prefix='/users')
admin_bp.register_blueprint(reference_bp, url_prefix='/reference')
admin_bp.register_blueprint(api_bp, url_prefix='/api')
admin_bp.register_blueprint(units_bp, url_prefix='/units')