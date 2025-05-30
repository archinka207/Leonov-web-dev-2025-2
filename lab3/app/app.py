import os
from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user

app = Flask(__name__)

app.config['SECRET_KEY'] = '34243214231523151325215323251'

app.config['REMEMBER_COOKIE_DURATION'] = 3600 * 24 * 365 


login_manager = LoginManager()
login_manager.init_app(app)

login_manager.login_view = 'login'

login_manager.login_message = "Для доступа к данной странице необходимо пройти процедуру аутентификации."
login_manager.login_message_category = "warning" 

class User(UserMixin):
    def __init__(self, id, username, password):
        self.id = id
        self.username = username
        self.password = password

    def check_password(self, password):
        return self.password == password

users = {
    "1": User(id="1", username="user", password="qwerty")
}

@login_manager.user_loader
def load_user(user_id):
    print(f"DEBUG: load_user called with user_id: {user_id}")
    user = users.get(user_id)
    if user:
        print(f"DEBUG: User {user.username} (ID: {user.id}) loaded successfully.")
    else:
        print(f"DEBUG: User with ID {user_id} not found.")
    return user

@app.route('/')
def index():
    return render_template('index.html', title='Главная страница')

@app.route('/counter')
def counter():

    if 'visits' in session:
        session['visits'] = session.get('visits') + 1
    else:
        session['visits'] = 1 # Если нет, устанавливаем на 1
    
    return render_template('counter.html', title='Счётчик посещений', visits=session['visits'])

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        flash('Вы уже вошли в систему.', 'info')
        return redirect(url_for('index'))

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        remember = bool(request.form.get('remember_me')) 

        user = None
        for u_obj in users.values():
            if u_obj.username == username:
                user = u_obj
                break

        if user and user.check_password(password):
            login_user(user, remember=remember)
            flash('Вы успешно вошли в систему!', 'success')
            
            next_page = request.args.get('next')
            print(f"DEBUG: Login successful. Redirecting to: {next_page or url_for('index')}")
            return redirect(next_page or url_for('index'))
        else:

            flash('Неверный логин или пароль.', 'danger')
            print(f"DEBUG: Login failed for username: {username}")
            return render_template('login.html', title='Вход')
    
    return render_template('login.html', title='Вход')

@app.route('/logout')
@login_required
def logout():
    logout_user() 
    flash('Вы вышли из системы.', 'info')
    print("DEBUG: User logged out.")
    return redirect(url_for('index'))

@app.route('/secret')
@login_required 
def secret_page():
    print(f"DEBUG: Accessing /secret. current_user.is_authenticated: {current_user.is_authenticated}")
    if current_user.is_authenticated:
        print(f"DEBUG: User {current_user.username} (ID: {current_user.id}) is authenticated on secret page.")
    else:
        print("DEBUG: User is NOT authenticated on secret page (this indicates an issue with Flask-Login setup or session).")

    return render_template('secret_page.html', title='Секретная страница')


if __name__ == '__main__':
    app.run(debug=True)