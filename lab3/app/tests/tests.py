import pytest
from app.app import app, users  # Импорт из app/app, так как app.py в папке app/app
from flask import url_for
from flask_login import current_user

# Фикстура для создания тестового клиента
@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        with app.app_context():
            yield client

# Тест 1: Проверка, что счётчик посещений увеличивается для одного пользователя
def test_counter_increments_on_each_visit(client):
    response = client.get('/counter')
    assert response.status_code == 200
    assert '1' in response.data.decode('utf-8')  # Первое посещение

    response = client.get('/counter')
    assert response.status_code == 200
    assert '2' in response.data.decode('utf-8')  # Второе посещение

# Тест 2: Проверка, что счётчик независим для разных клиентов
def test_counter_is_independent_for_different_clients(client):
    response = client.get('/counter')
    assert '1' in response.data.decode('utf-8')

    with app.test_client() as client2:
        response = client2.get('/counter')
        assert '1' in response.data.decode('utf-8')  # Новая сессия начинается с 1

# Тест 3: Проверка доступа аутентифицированного пользователя к секретной странице
def test_authenticated_user_access_secret(client):
    client.post('/login', data={'username': 'user', 'password': 'qwerty'})
    response = client.get('/secret')
    assert response.status_code == 200
    assert 'Секретная страница' in response.data.decode('utf-8')

# Тест 4: Проверка перенаправления неаутентифицированного пользователя на страницу логина
def test_anonymous_user_redirected_to_login(client):
    response = client.get('/secret', follow_redirects=True)
    assert response.status_code == 200
    assert 'Вход' in response.data.decode('utf-8')
    assert 'Для доступа к данной странице необходимо пройти процедуру аутентификации.' in response.data.decode('utf-8')

# Тест 5: Проверка перенаправления на секретную страницу после успешного логина
def test_redirect_after_successful_login(client):
    response = client.get('/secret', follow_redirects=False)
    assert response.status_code == 302
    assert 'next=%2Fsecret' in response.location

    response = client.post('/login', data={'username': 'user', 'password': 'qwerty'}, follow_redirects=True)
    assert response.status_code == 200
    assert 'Секретная страница' in response.data.decode('utf-8')

# Тест 6: Проверка функциональности "Запомнить меня"
def test_remember_me_functionality(client):
    response = client.post('/login', data={
        'username': 'user',
        'password': 'qwerty',
        'remember_me': 'y'
    }, follow_redirects=True)
    assert response.status_code == 200
    cookies = response.headers.getlist('Set-Cookie')
    assert any('session=' in cookie for cookie in cookies)  # Проверяем наличие session cookie
    assert 'Вы успешно вошли в систему!' in response.data.decode('utf-8')

# Тест 7: Проверка отображения ошибки при неверном логине
def test_failed_login_shows_error(client):
    response = client.post('/login', data={'username': 'wrong_user', 'password': 'qwerty'})
    assert response.status_code == 200
    assert 'Неверный логин или пароль.' in response.data.decode('utf-8')
    assert 'Вход' in response.data.decode('utf-8')

# Тест 8: Проверка успешного логина с перенаправлением и flash-сообщением
def test_successful_login_redirect_and_flash(client):
    response = client.post('/login', data={'username': 'user', 'password': 'qwerty'}, follow_redirects=True)
    assert response.status_code == 200
    assert 'Главная страница' in response.data.decode('utf-8')
    assert 'Вы успешно вошли в систему!' in response.data.decode('utf-8')

# Тест 9: Проверка, что при неверном пароле пользователь остаётся на странице логина
def test_failed_login_stays_with_error(client):
    response = client.post('/login', data={'username': 'user', 'password': 'wrong'})
    assert response.status_code == 200
    assert 'Неверный логин или пароль.' in response.data.decode('utf-8')
    assert 'Вход' in response.data.decode('utf-8')

# Тест 10: Проверка выхода из системы
def test_logout_functionality(client):
    client.post('/login', data={'username': 'user', 'password': 'qwerty'})
    response = client.get('/logout', follow_redirects=True)
    assert response.status_code == 200
    assert 'Вы вышли из системы.' in response.data.decode('utf-8')
    assert 'Главная страница' in response.data.decode('utf-8')

def test_remember_cookie_properties(client):
    response = client.post('/login', data={
        'username': 'user',
        'password': 'qwerty',
        'remember_me': 'y'
    })
    cookies = response.headers.getlist('Set-Cookie')
    assert any('session=' in cookie for cookie in cookies)  # Проверяем наличие session cookie
    assert any('Expires=' in cookie for cookie in cookies)  # Проверяем наличие Expires

# Тест 12: Проверка отображения ссылки на секретную страницу в навбаре
def test_navbar_links(client):
    # Для неаутентифицированного пользователя
    response = client.get('/')
    assert 'href="/secret"' not in response.data.decode('utf-8')  # Ссылка отсутствует

    # Для аутентифицированного пользователя
    client.post('/login', data={'username': 'user', 'password': 'qwerty'})
    response = client.get('/')
    assert 'href="/secret"' in response.data.decode('utf-8')