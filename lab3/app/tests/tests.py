import os
import shutil
import tempfile
import unittest
from app import app, users, User, login_manager 
from flask import get_flashed_messages, url_for, session, request # Добавлен request

# Содержимое для базовых HTML-шаблонов (остается таким же, как раньше)
TEMPLATES_CONTENT = {
    "base.html": """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>{{ title }}</title>
</head>
<body>
    <nav>
        <a href="{{ url_for('index') }}">Главная</a>
        <a href="{{ url_for('counter') }}">Счетчик</a>
        {% if current_user.is_authenticated %}
            <a href="{{ url_for('secret_page') }}" id="secret-link">Секретная страница</a>
            <a href="{{ url_for('logout') }}" id="logout-link">Выход</a>
        {% else %}
            <a href="{{ url_for('login') }}" id="login-link">Вход</a>
        {% endif %}
    </nav>
    <hr>
    {% with messages = get_flashed_messages(with_categories=true) %}
        {% if messages %}
            <ul id="flash-messages">
            {% for category, message in messages %}
                <li class="{{ category }}">{{ message }}</li>
            {% endfor %}
            </ul>
        {% endif %}
    {% endwith %}
    {% block content %}{% endblock %}
</body>
</html>
    """,
    "index.html": """
{% extends "base.html" %}
{% block content %}
    <h1>{{ title }}</h1>
    <p>Добро пожаловать!</p>
    <p id="index-content">Содержимое главной страницы</p>
{% endblock %}
    """,
    "counter.html": """
{% extends "base.html" %}
{% block content %}
    <h1>{{ title }}</h1>
    <p>Эту страницу вы посетили <span id="visits-count">{{ visits }}</span> раз(а).</p>
{% endblock %}
    """,
    "login.html": """
{% extends "base.html" %}
{% block content %}
    <h1>{{ title }}</h1>
    <form method="POST" action="{{ url_for('login') }}{% if request.args.next %}?next={{ request.args.next | urlencode }}{% endif %}">
        <p>
            <label for="username">Логин:</label>
            <input type="text" id="username" name="username" required>
        </p>
        <p>
            <label for="password">Пароль:</label>
            <input type="password" id="password" name="password" required>
        </p>
        <p>
            <input type="checkbox" id="remember_me" name="remember_me">
            <label for="remember_me">Запомнить меня</label>
        </p>
        <p><input type="submit" value="Войти"></p>
    </form>
    <p id="login-page-identifier">Это страница входа.</p>
{% endblock %}
    """,
    "secret_page.html": """
{% extends "base.html" %}
{% block content %}
    <h1>{{ title }}</h1>
    <p id="secret-content">Это секретная информация, доступная только вам!</p>
{% endblock %}
    """
}

class TestFlaskApp(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.temp_dir = tempfile.mkdtemp()
        app.template_folder = cls.temp_dir
        for filename, content in TEMPLATES_CONTENT.items():
            with open(os.path.join(cls.temp_dir, filename), 'w', encoding='utf-8') as f:
                f.write(content)
        
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False 
        app.config['SECRET_KEY'] = 'test_secret_key_for_sessions'
        app.config['SERVER_NAME'] = 'localhost.test' 
        app.config['APPLICATION_ROOT'] = '/'
        app.config['PREFERRED_URL_SCHEME'] = 'http'
        
        app.config['REMEMBER_COOKIE_DURATION'] = 60 
        app.config['REMEMBER_COOKIE_NAME'] = 'test_remember_token'
        
        login_manager.remember_cookie_name = app.config['REMEMBER_COOKIE_NAME']
        login_manager.remember_cookie_duration = app.config['REMEMBER_COOKIE_DURATION']

        if "1" not in users:
             users["1"] = User(id="1", username="user", password="qwerty")

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.temp_dir)

    def setUp(self):
        self.app_context = app.app_context()
        self.app_context.push()
        self.client = app.test_client()
        
        with self.client.session_transaction() as sess:
            sess.clear()

    def tearDown(self):
        with self.client:
            if 'user_id' in session:
                 self.client.get(url_for('logout'))
        self.app_context.pop()

    def _login(self, username, password, remember=False, next_url=None):
        data = {'username': username, 'password': password}
        if remember:
            data['remember_me'] = 'on'
        
        with app.test_request_context():
            login_target_url = url_for('login')
            if next_url:
                login_target_url += f"?next={next_url}" 
            
        return self.client.post(login_target_url, data=data, follow_redirects=True)

    def _logout(self):
        with app.test_request_context():
            logout_url = url_for('logout')
        return self.client.get(logout_url, follow_redirects=True)

    # --- Тесты ---

    def test_counter_increments_for_single_client(self):
        with self.client:
            response = self.client.get(url_for('counter'))
            self.assertIn('<span id="visits-count">1</span>', response.data.decode('utf-8'))
            
            response = self.client.get(url_for('counter'))
            self.assertIn('<span id="visits-count">2</span>', response.data.decode('utf-8'))
            
            response = self.client.get(url_for('counter'))
            self.assertIn('<span id="visits-count">3</span>', response.data.decode('utf-8'))

    def test_counter_is_separate_for_different_clients(self):
        client1 = app.test_client()
        client2 = app.test_client()

        with client1:
            response1 = client1.get(url_for('counter'))
            self.assertIn('<span id="visits-count">1</span>', response1.data.decode('utf-8'))
            response1 = client1.get(url_for('counter'))
            self.assertIn('<span id="visits-count">2</span>', response1.data.decode('utf-8'))

        with client2:
            response2 = client2.get(url_for('counter'))
            self.assertIn('<span id="visits-count">1</span>', response2.data.decode('utf-8'))

        with client1:
            response1_again = client1.get(url_for('counter'))
            self.assertIn('<span id="visits-count">3</span>', response1_again.data.decode('utf-8'))
            
    def test_successful_login_redirects_to_index_and_flashes_message(self):
        with self.client:
            response = self._login('user', 'qwerty')
            self.assertEqual(response.status_code, 200)
            self.assertIn('<p id="index-content">Содержимое главной страницы</p>', response.data.decode('utf-8'))
            
            flashed_messages = get_flashed_messages(with_categories=True)
            self.assertIn(('success', 'Вы успешно вошли в систему!'), flashed_messages)

    def test_failed_login_stays_on_login_page_and_flashes_error(self):
        with self.client:
            response = self.client.post(url_for('login'), data={
                'username': 'user',
                'password': 'wrongpassword'
            }, follow_redirects=False)
            
            self.assertEqual(response.status_code, 200) 
            response_text = response.data.decode('utf-8')
            self.assertIn('<p id="login-page-identifier">Это страница входа.</p>', response_text)
            self.assertIn('<li class="danger">Неверный логин или пароль.</li>', response_text)

    def test_authenticated_user_can_access_secret_page(self):
        with self.client:
            self._login('user', 'qwerty')
            response = self.client.get(url_for('secret_page'))
            self.assertEqual(response.status_code, 200)
            self.assertIn('<p id="secret-content">Это секретная информация', response.data.decode('utf-8'))

    def test_unauthenticated_user_redirected_from_secret_to_login_with_message_and_next_param(self):
        with self.client:
            secret_page_url = url_for('secret_page')
            response_secret_attempt = self.client.get(secret_page_url, follow_redirects=False) 
            self.assertEqual(response_secret_attempt.status_code, 302)
            
            login_url_base = url_for('login')
            self.assertTrue(response_secret_attempt.location.startswith(login_url_base))
            # Убедимся, что параметр next содержит правильный путь к секретной странице
            self.assertIn(f"next={secret_page_url}", response_secret_attempt.location)

            response_login_page = self.client.get(response_secret_attempt.location, follow_redirects=True)
            self.assertIn(
                '<li class="warning">Для доступа к данной странице необходимо пройти процедуру аутентификации.</li>',
                response_login_page.data.decode('utf-8')
            )

    def test_login_after_redirect_from_secret_goes_to_secret(self):
        with self.client:
            secret_page_url = url_for('secret_page')
            # Первый запрос для установки 'next' параметра при редиректе
            self.client.get(secret_page_url, follow_redirects=False) 
            
            response = self._login('user', 'qwerty', next_url=secret_page_url)

            self.assertEqual(response.status_code, 200)
            # Проверяем, что текущий URL после логина - это секретная страница
            self.assertEqual(request.path, secret_page_url)
            self.assertIn('<p id="secret-content">Это секретная информация', response.data.decode('utf-8')) 
            self.assertNotIn('<p id="index-content">', response.data.decode('utf-8'))

    def test_login_with_remember_me_sets_cookie(self):
        with self.client:
            response = self._login('user', 'qwerty', remember=True)
            
            remember_cookie_header_value = None
            for header_val in response.headers.getlist('Set-Cookie'):
                if app.config['REMEMBER_COOKIE_NAME'] in header_val:
                    remember_cookie_header_value = header_val
                    break
            
            self.assertIsNotNone(remember_cookie_header_value, "Cookie 'Запомнить меня' не установлена.")
            self.assertIn(f"Max-Age={app.config['REMEMBER_COOKIE_DURATION']}", remember_cookie_header_value)
            self.assertIn("HttpOnly", remember_cookie_header_value)

    def test_navbar_links_for_anonymous_user_on_index(self):
        with self.client:
            response = self.client.get(url_for('index'))
            response_text = response.data.decode('utf-8')
            self.assertIn(f'<a href="{url_for("login")}" id="login-link">Вход</a>', response_text)
            self.assertNotIn(f'<a href="{url_for("secret_page")}" id="secret-link">', response_text)
            self.assertNotIn(f'<a href="{url_for("logout")}" id="logout-link">', response_text)

    def test_navbar_links_for_authenticated_user_on_index(self):
        with self.client:
            self._login('user', 'qwerty')
            response = self.client.get(url_for('index'))
            response_text = response.data.decode('utf-8')
            self.assertNotIn(f'<a href="{url_for("login")}" id="login-link">', response_text)
            self.assertIn(f'<a href="{url_for("secret_page")}" id="secret-link">Секретная страница</a>', response_text)
            self.assertIn(f'<a href="{url_for("logout")}" id="logout-link">Выход</a>', response_text)

    def test_logout_redirects_to_index_flashes_message_and_denies_secret(self):
        with self.client:
            self._login('user', 'qwerty')
            # Убедимся, что доступ к секретной странице есть
            self.assertEqual(self.client.get(url_for('secret_page')).status_code, 200)

            response = self._logout() # Выходим
            self.assertEqual(response.status_code, 200)
            self.assertIn('<p id="index-content">Содержимое главной страницы</p>', response.data.decode('utf-8'))
            
            flashed_messages = get_flashed_messages(with_categories=True)
            self.assertIn(('info', 'Вы вышли из системы.'), flashed_messages)

            # Проверяем, что после выхода доступ к секретной странице закрыт (редирект на логин)
            secret_response_after_logout = self.client.get(url_for('secret_page'), follow_redirects=False)
            self.assertEqual(secret_response_after_logout.status_code, 302)
            login_url = url_for('login')
            self.assertTrue(secret_response_after_logout.location.startswith(login_url))

    def test_already_logged_in_user_redirected_from_login_page(self):
        with self.client:
            self._login('user', 'qwerty')
            response = self.client.get(url_for('login'), follow_redirects=True)
            self.assertEqual(response.status_code, 200)
            # Убедимся, что мы на главной странице
            self.assertIn('<p id="index-content">Содержимое главной страницы</p>', response.data.decode('utf-8')) 
            # И что на странице нет идентификатора страницы входа
            self.assertNotIn('<p id="login-page-identifier">', response.data.decode('utf-8'))


            flashed_messages = get_flashed_messages(with_categories=True)
            self.assertIn(('info', 'Вы уже вошли в систему.'), flashed_messages)

if __name__ == '__main__':
    unittest.main(argv=['first-arg-is-ignored'], exit=False)