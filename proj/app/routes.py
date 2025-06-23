# app/routes.py

import os
import bleach
from werkzeug.utils import secure_filename
from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_user, logout_user, login_required, current_user
from sqlalchemy import case, func
from app import db
from app.models import User, Animal, Photo, Adoption, Role
from app.forms import LoginForm, AnimalForm, AdoptionForm, RegistrationForm
from app.decorators import roles_required

bp = Blueprint('routes', __name__)

ALLOWED_TAGS = ['p', 'strong', 'em', 'ul', 'ol', 'li', 'a', 'h1', 'h2', 'h3', 'br', 'blockquote']

@bp.route('/')
def index():
    page = request.args.get('page', 1, type=int)
    
    status_order = case(
        (Animal.status == 'available', 1),
        (Animal.status == 'adoption', 2),
        (Animal.status == 'adopted', 3),
        else_=4
    )
    
    animals_pagination = db.session.query(Animal).order_by(status_order, Animal.created_at.desc()).paginate(
        page=page, per_page=9, error_out=False
    )
    return render_template('index.html', animals=animals_pagination, title='Главная')

# --- АУТЕНТИФИКАЦИЯ И РЕГИСТРАЦИЯ ---

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('routes.index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = db.session.scalar(db.select(User).where(User.login == form.login.data))
        if user is None or not user.check_password(form.password.data):
            flash('Невозможно аутентифицироваться с указанными логином и паролем', 'danger')
            return redirect(url_for('routes.login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or not next_page.startswith('/'):
            next_page = url_for('routes.index')
        return redirect(next_page)
    return render_template('auth/login.html', title='Вход', form=form)

@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('routes.index'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        try:
            user_role = Role.query.filter_by(name='user').first()
            if not user_role:
                flash('Роль "user" не найдена. Обратитесь к администратору.', 'danger')
                return redirect(url_for('routes.register'))

            new_user = User(
                login=form.login.data,
                first_name=form.first_name.data,
                last_name=form.last_name.data,
                middle_name=form.middle_name.data,
                role_id=user_role.id
            )
            new_user.set_password(form.password.data)
            
            db.session.add(new_user)
            db.session.commit()
            
            flash('Вы успешно зарегистрировались! Теперь можете войти.', 'success')
            return redirect(url_for('routes.login'))
        except Exception as e:
            db.session.rollback()
            flash(f'Во время регистрации произошла ошибка: {e}', 'danger')

    return render_template('auth/register.html', title='Регистрация', form=form)

@bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('routes.index'))

# --- ПРОСМОТР ЖИВОТНЫХ ---

@bp.route('/animal/<int:animal_id>')
def view_animal(animal_id):
    animal = db.session.get(Animal, animal_id)
    if not animal:
        flash('Животное не найдено.', 'danger')
        return redirect(url_for('routes.index'))

    user_application = None
    if current_user.is_authenticated and current_user.role.name == 'user':
        user_application = db.session.scalar(
            db.select(Adoption).where(Adoption.animal_id == animal.id, Adoption.user_id == current_user.id)
        )

    # --- ИЗМЕНЕНИЕ ЗДЕСЬ ---
    # Готовим отсортированный список заявок здесь, а не в шаблоне
    sorted_adoptions = []
    if current_user.is_authenticated and (current_user.is_admin or current_user.is_moderator):
        sorted_adoptions = animal.adoptions.order_by(Adoption.application_date.desc()).all()

    adoption_form = AdoptionForm()
    
    # Передаем готовый список в шаблон
    return render_template(
        'animal.html', 
        title=animal.name, 
        animal=animal, 
        user_application=user_application,
        adoption_form=adoption_form,
        adoptions=sorted_adoptions  # <-- Новая переменная
    )
    # -------------------------

# --- УПРАВЛЕНИЕ ЖИВОТНЫМИ (ДЛЯ АДМИНОВ И МОДЕРАТОРОВ) ---

@bp.route('/animal/add', methods=['GET', 'POST'])
@login_required
@roles_required(['admin'])
def add_animal():
    form = AnimalForm()
    if form.validate_on_submit():
        try:
            cleaned_description = bleach.clean(form.description.data, tags=ALLOWED_TAGS, strip=True)
            
            new_animal = Animal(
                name=form.name.data,
                description=cleaned_description,
                age_in_months=form.age_in_months.data,
                breed=form.breed.data,
                gender=form.gender.data,
                status=form.status.data
            )
            db.session.add(new_animal)
            db.session.flush()

            files = request.files.getlist(form.images.name)
            for file in files:
                if file and file.filename != '':
                    filename = secure_filename(file.filename)
                    file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
                    file.save(file_path)
                    
                    new_photo = Photo(filename=filename, mimetype=file.mimetype, animal_id=new_animal.id)
                    db.session.add(new_photo)
            
            db.session.commit()
            flash('Животное успешно добавлено!', 'success')
            return redirect(url_for('routes.view_animal', animal_id=new_animal.id))
        except Exception as e:
            db.session.rollback()
            flash(f'При сохранении данных возникла ошибка: {e}. Проверьте корректность введённых данных.', 'danger')
            
    return render_template('animal_form.html', title='Добавить животное', form=form, is_edit=False)


@bp.route('/animal/<int:animal_id>/edit', methods=['GET', 'POST'])
@login_required
@roles_required(['admin', 'moderator'])
def edit_animal(animal_id):
    animal = db.session.get(Animal, animal_id)
    if not animal:
        flash('Животное не найдено.', 'danger')
        return redirect(url_for('routes.index'))
    
    form = AnimalForm(obj=animal)
    del form.images

    if form.validate_on_submit():
        try:
            animal.name = form.name.data
            animal.description = bleach.clean(form.description.data, tags=ALLOWED_TAGS, strip=True)
            animal.age_in_months = form.age_in_months.data
            animal.breed = form.breed.data
            animal.gender = form.gender.data
            animal.status = form.status.data
            db.session.commit()
            flash('Данные о животном успешно обновлены!', 'success')
            return redirect(url_for('routes.view_animal', animal_id=animal.id))
        except Exception as e:
            db.session.rollback()
            flash(f'При обновлении данных возникла ошибка: {e}', 'danger')

    return render_template('animal_form.html', title='Редактировать животное', form=form, is_edit=True)

@bp.route('/animal/<int:animal_id>/delete', methods=['POST'])
@login_required
@roles_required(['admin'])
def delete_animal(animal_id):
    animal = db.session.get(Animal, animal_id)
    if animal:
        try:
            animal_name = animal.name
            for photo in animal.photos:
                file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], photo.filename)
                if os.path.exists(file_path):
                    os.remove(file_path)
            
            db.session.delete(animal)
            db.session.commit()
            flash(f'Животное "{animal_name}" и все связанные данные удалены.', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Произошла ошибка при удалении: {e}', 'danger')
    else:
        flash('Животное не найдено.', 'danger')
    return redirect(url_for('routes.index'))

# --- УПРАВЛЕНИЕ ЗАЯВКАМИ НА УСЫНОВЛЕНИЕ ---

@bp.route('/animal/<int:animal_id>/apply', methods=['POST'])
@login_required
@roles_required(['user'])
def apply_for_adoption(animal_id):
    animal = db.session.get(Animal, animal_id)
    if not animal or animal.status == 'adopted':
        flash('Это животное уже нашло дом.', 'warning')
        return redirect(url_for('routes.view_animal', animal_id=animal_id))

    existing_application = db.session.scalar(
        db.select(Adoption).where(Adoption.animal_id == animal.id, Adoption.user_id == current_user.id)
    )
    if existing_application:
        flash('Вы уже подавали заявку на это животное.', 'info')
        return redirect(url_for('routes.view_animal', animal_id=animal_id))
    
    form = AdoptionForm()
    if form.validate_on_submit():
        try:
            application = Adoption(
                animal_id=animal_id,
                user_id=current_user.id,
                contact_info=form.contact_info.data
            )
            if animal.status == 'available':
                 animal.status = 'adoption'
            
            db.session.add(application)
            db.session.commit()
            flash('Ваша заявка на усыновление успешно отправлена!', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Произошла ошибка при отправке заявки: {e}', 'danger')
    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f"Ошибка в поле '{getattr(form, field).label.text}': {error}", 'danger')

    return redirect(url_for('routes.view_animal', animal_id=animal_id))

@bp.route('/adoption/<int:adoption_id>/<action>', methods=['POST'])
@login_required
@roles_required(['admin', 'moderator'])
def handle_adoption(adoption_id, action):
    application = db.session.get(Adoption, adoption_id)
    if not application:
        flash('Заявка не найдена.', 'danger')
        return redirect(request.referrer or url_for('routes.index'))

    animal = application.animal
    try:
        if action == 'accept':
            application.status = 'accepted'
            animal.status = 'adopted'
            
            db.session.query(Adoption).filter(
                Adoption.animal_id == animal.id,
                Adoption.status == 'pending'
            ).update({'status': 'rejected_adopted'})
            
            flash('Заявка одобрена. Животное обрело дом!', 'success')

        elif action == 'reject':
            application.status = 'rejected'
            
            pending_count = db.session.scalar(db.select(func.count(Adoption.id)).where(
                Adoption.animal_id == animal.id,
                Adoption.status == 'pending'
            ))
            if pending_count == 0 and animal.status != 'adopted':
                animal.status = 'available'

            flash('Заявка отклонена.', 'info')
        
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        flash(f'Произошла ошибка при обработке заявки: {e}', 'danger')

    return redirect(url_for('routes.view_animal', animal_id=animal.id))