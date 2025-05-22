import pytest
from app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_url_params_display(client):
    """Проверяет отображение параметров URL"""
    response = client.get('/url?param1=value1&param2=value2')
    assert response.status_code == 200
    html = response.data.decode('utf-8')
    assert 'param1' in html
    assert 'value1' in html

def test_url_params_no_params(client):
    """Проверяет страницу без параметров URL"""
    response = client.get('/url')
    assert response.status_code == 200
    html = response.data.decode('utf-8')
    assert 'Параметры URL' in html

def test_headers_display(client):
    """Проверяет отображение заголовков"""
    response = client.get('/headers', headers={'User-Agent': 'TestClient'})
    assert response.status_code == 200
    html = response.data.decode('utf-8')
    assert 'User-Agent' in html
    assert 'TestClient' in html

def test_cookies_set_and_delete(client):
    """Проверяет установку и удаление куки"""
    # Первый запрос - проверяем установку куки
    response1 = client.get('/cookies')
    assert response1.status_code == 200
    assert 'my_cookie=flask_value' in response1.headers.get('Set-Cookie', '')
    
    # Второй запрос - проверяем удаление куки
    response2 = client.get('/cookies')
    assert 'my_cookie=;' in response2.headers.get('Set-Cookie', '')

def test_form_get_display(client):
    """Проверяет GET-запрос формы"""
    response = client.get('/form')
    assert response.status_code == 200
    html = response.data.decode('utf-8')
    assert 'Параметры формы' in html

def test_form_post_display(client):
    """Проверяет POST-запрос формы"""
    data = {'field1': 'Test Value', 'field2': 'City Name'}
    response = client.post('/form', data=data)
    assert response.status_code == 200
    html = response.data.decode('utf-8')
    assert 'Test Value' in html
    assert 'City Name' in html

@pytest.mark.parametrize("phone_input,expected", [
    ("+7 (123) 456-75-90", "8-123-456-75-90"),
    ("8(123)4567590", "8-123-456-75-90"),
    ("123.456.75.90", "8-123-456-75-90"),
    ("9123456789", "8-912-345-67-89"),
    ("8 999 123 45 67", "8-999-123-45-67"),
])
def test_phone_valid_formats(client, phone_input, expected):
    """Проверяет валидные форматы телефона"""
    response = client.post('/phone', data={'phone_number': phone_input})
    assert response.status_code == 200
    html = response.data.decode('utf-8')
    assert expected in html
    assert 'is-invalid' not in html

@pytest.mark.parametrize("phone_input,error_msg", [
    ("123", "Недопустимый ввод. Неверное количество цифр."),
    ("123456789012", "Недопустимый ввод. Неверное количество цифр."),
    ("+7123456789", "Недопустимый ввод. Неверное количество цифр."),
    ("8123456789", "Недопустимый ввод. Неверное количество цифр."),
])
def test_phone_invalid_length(client, phone_input, error_msg):
    """Проверяет неверную длину номера"""
    response = client.post('/phone', data={'phone_number': phone_input})
    assert response.status_code == 200
    html = response.data.decode('utf-8')
    assert error_msg in html
    assert 'is-invalid' in html

@pytest.mark.parametrize("phone_input,error_msg", [
    ("8999123456A", "Недопустимый ввод. В номере телефона встречаются недопустимые символы."),
    ("abc", "Недопустимый ввод. В номере телефона встречаются недопустимые символы."),
])
def test_phone_invalid_chars(client, phone_input, error_msg):
    """Проверяет недопустимые символы"""
    response = client.post('/phone', data={'phone_number': phone_input})
    assert response.status_code == 200
    html = response.data.decode('utf-8')
    assert error_msg in html
    assert 'is-invalid' in html

def test_phone_empty_input(client):
    """Проверяет пустой ввод"""
    response = client.post('/phone', data={'phone_number': ''})
    assert response.status_code == 200
    html = response.data.decode('utf-8')
    # Проверяем наличие класса ошибки и сообщения
    assert 'is-invalid' in html
    assert 'invalid-feedback' in html
    # Проверяем, что выводится какое-то сообщение об ошибке
    assert 'Недопустимый ввод' in html

def test_phone_bootstrap_classes(client):
    """Проверяет классы Bootstrap при ошибке"""
    response = client.post('/phone', data={'phone_number': 'invalid'})
    assert response.status_code == 200
    html = response.data.decode('utf-8')
    assert 'is-invalid' in html
    assert 'invalid-feedback' in html