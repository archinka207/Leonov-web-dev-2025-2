# init_db.py

import click
from flask.cli import with_appcontext
from app import db
from app.models import Role, User
from werkzeug.security import generate_password_hash

# Создаем новую команду с именем 'init-db'
@click.command('init-db')
@with_appcontext
def init_db_command():
    """Очищает существующие данные и создает новые таблицы."""
    print("Проверка и создание таблиц в базе данных PostgreSQL...")
    # Эта команда создаст все таблицы на основе моделей из models.py
    # Если таблицы уже существуют, она ничего не сделает.
    db.create_all()
    print("Проверка таблиц завершена.")

    # --- Создание ролей, если их еще нет ---
    if not Role.query.filter_by(name='admin').first():
        print("Роли не найдены. Создание ролей...")
        admin_role = Role(name='admin', description='Администратор')
        moderator_role = Role(name='moderator', description='Модератор')
        user_role = Role(name='user', description='Пользователь')
        db.session.add_all([admin_role, moderator_role, user_role])
        db.session.commit()
        print("Роли 'admin', 'moderator', 'user' успешно созданы.")
    else:
        print("Роли уже существуют в базе данных.")
        admin_role = Role.query.filter_by(name='admin').first()

    # --- Создание пользователя-администратора, если его еще нет ---
    if not User.query.filter_by(login='admin').first():
        print("Пользователь 'admin' не найден. Создание...")
        admin_user = User(
            login='admin',
            last_name='Админов',
            first_name='Админ',
            middle_name='Админович',
            role_id=admin_role.id # Связываем с ролью админа
        )
        # Устанавливаем пароль (никогда не храните пароли в открытом виде!)
        admin_user.set_password('superpassword123')
        
        db.session.add(admin_user)
        db.session.commit()
        print("Пользователь 'admin' с паролем 'superpassword123' успешно создан.")
    else:
        print("Пользователь 'admin' уже существует в базе данных.")

    click.echo('\nИнициализация базы данных завершена.')