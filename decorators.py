from functools import wraps
from flask import session, flash, redirect, url_for

def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get('user_id'):
            flash('Необходимо войти в систему', 'warning')
            return redirect(url_for('main.login'))
        
        if session.get('role') != 'admin':
            flash('Доступ запрещён. Требуются права администратора.', 'danger')
            return redirect(url_for('main.index'))
        
        return f(*args, **kwargs)
    return decorated

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get('user_id'):
            flash('Пожалуйста, войдите в систему', 'warning')
            return redirect(url_for('main.login'))
        return f(*args, **kwargs)
    return decorated