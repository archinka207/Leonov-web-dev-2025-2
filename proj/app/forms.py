# app/forms.py

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField, IntegerField, SelectField, MultipleFileField
from wtforms.validators import DataRequired, Length, NumberRange, Email, EqualTo, ValidationError
from .models import User

# Форма для входа
class LoginForm(FlaskForm):
    login = StringField('Логин', validators=[DataRequired(), Length(max=64)])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')

# Форма регистрации
class RegistrationForm(FlaskForm):
    login = StringField('Логин', validators=[DataRequired(), Length(min=4, max=64)])
    first_name = StringField('Имя', validators=[DataRequired(), Length(max=64)])
    last_name = StringField('Фамилия', validators=[DataRequired(), Length(max=64)])
    middle_name = StringField('Отчество (необязательно)', validators=[Length(max=64)])
    password = PasswordField('Пароль', validators=[DataRequired(), Length(min=6)])
    password2 = PasswordField(
        'Повторите пароль', validators=[DataRequired(), EqualTo('password', message='Пароли должны совпадать.')])
    submit = SubmitField('Зарегистрироваться')

    def validate_login(self, login):
        user = User.query.filter_by(login=login.data).first()
        if user is not None:
            raise ValidationError('Этот логин уже занят. Пожалуйста, выберите другой.')

# Форма для добавления/редактирования животного
class AnimalForm(FlaskForm):
    name = StringField('Имя', validators=[DataRequired(), Length(min=2, max=100)])
    description = TextAreaField('Описание (поддерживает Markdown)', validators=[DataRequired()])
    age_in_months = IntegerField('Возраст (в месяцах)', validators=[DataRequired(), NumberRange(min=1, message="Возраст должен быть положительным числом.")])
    breed = StringField('Порода', validators=[DataRequired(), Length(max=100)])
    gender = SelectField('Пол', choices=[('male', 'Мальчик'), ('female', 'Девочка')], validators=[DataRequired()])
    status = SelectField('Статус', choices=[
        ('available', 'Доступно для усыновления'),
        ('adoption', 'В процессе усыновления'),
        ('adopted', 'Усыновлён')
    ], default='available', validators=[DataRequired()])
    # Вот наше поле, его тип - MultipleFileField, и это ключ к решению
    images = MultipleFileField('Фотографии (можно выбрать несколько)')
    submit = SubmitField('Сохранить')

# Форма для подачи заявки на усыновление
class AdoptionForm(FlaskForm):
    contact_info = TextAreaField('Ваши контактные данные (телефон, email и т.д.)', validators=[DataRequired(), Length(min=10, max=255)])
    submit = SubmitField('Отправить заявку')