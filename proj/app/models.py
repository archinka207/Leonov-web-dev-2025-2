# app/models.py

from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import db, login_manager

# Таблица ролей
class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=False)
    users = db.relationship('User', backref='role', lazy='dynamic')

    def __repr__(self):
        return f'<Role {self.name}>'

# Таблица пользователей
class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(64), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    last_name = db.Column(db.String(64), nullable=False)
    first_name = db.Column(db.String(64), nullable=False)
    middle_name = db.Column(db.String(64))
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'), nullable=False)
    adoptions = db.relationship('Adoption', backref='user', lazy='dynamic', cascade="all, delete-orphan")

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @property
    def is_admin(self):
        return self.role.name == 'admin'

    @property
    def is_moderator(self):
        return self.role.name == 'moderator'

    def __repr__(self):
        return f'<User {self.login}>'

# Загрузчик пользователей для Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

# Таблица животных
class Animal(db.Model):
    __tablename__ = 'animals'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    age_in_months = db.Column(db.Integer, nullable=False)
    breed = db.Column(db.String(100), nullable=False)
    gender = db.Column(db.String(10), nullable=False)
    status = db.Column(db.String(20), nullable=False, default='available', index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    
    photos = db.relationship('Photo', backref='animal', lazy='dynamic', cascade="all, delete-orphan")
    adoptions = db.relationship('Adoption', backref='animal', lazy='dynamic', cascade="all, delete-orphan")

    def __repr__(self):
        return f'<Animal {self.name}>'

# Таблица фотографий
class Photo(db.Model):
    __tablename__ = 'photos'
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    mimetype = db.Column(db.String(255), nullable=False)
    animal_id = db.Column(db.Integer, db.ForeignKey('animals.id', ondelete='CASCADE'), nullable=False)

    def __repr__(self):
        return f'<Photo {self.filename}>'

# Таблица усыновлений (заявок)
class Adoption(db.Model):
    __tablename__ = 'adoptions'
    id = db.Column(db.Integer, primary_key=True)
    animal_id = db.Column(db.Integer, db.ForeignKey('animals.id', ondelete='CASCADE'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    application_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, index=True)
    status = db.Column(db.String(20), nullable=False, default='pending', index=True)
    contact_info = db.Column(db.String(255), nullable=False)

    def __repr__(self):
        return f'<Adoption user_id={self.user_id} animal_id={self.animal_id}>'