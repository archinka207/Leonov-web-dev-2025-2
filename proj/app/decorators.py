# app/decorators.py

from functools import wraps
from flask import flash, redirect, url_for
from flask_login import current_user

def roles_required(roles):
    """
    Декоратор для проверки, имеет ли текущий пользователь одну из требуемых ролей.
    :param roles: Список строк с названиями ролей, которым разрешен доступ.
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                flash('Для выполнения данного действия необходимо пройти процедуру аутентификации.', 'warning')
                return redirect(url_for('routes.login'))

            if current_user.role.name not in roles:
                flash('У вас недостаточно прав для выполнения данного действия.', 'danger')
                return redirect(url_for('routes.index'))
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator