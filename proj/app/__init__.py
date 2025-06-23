# app/__init__.py (новая версия)

import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
# from flask_bootstrap import Bootstrap5 # <-- УДАЛЯЕМ
from flask_migrate import Migrate
import markdown
from config import Config

db = SQLAlchemy()
login_manager = LoginManager()

migrate = Migrate()

login_manager.login_view = 'routes.login'
login_manager.login_message = 'Для выполнения данного действия необходимо пройти процедуру аутентификации'
login_manager.login_message_category = 'warning'

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    upload_folder = app.config['UPLOAD_FOLDER']
    if not os.path.exists(upload_folder):
        os.makedirs(upload_folder)

    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    
    def markdown_to_html(text):
        return markdown.markdown(text)
    app.jinja_env.filters['markdown'] = markdown_to_html

    from app.routes import bp as routes_bp
    app.register_blueprint(routes_bp)

    return app

from app import models