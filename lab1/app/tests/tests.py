import pytest
import sys
import os
from app import posts_list 
app_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../app'))
sys.path.insert(0, app_path)

from app import app as flask_app
from datetime import datetime
from flask import template_rendered

# Фикстуры для тестирования
@pytest.fixture
def app():
    flask_app.config['TESTING'] = True
    yield flask_app

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def captured_templates(app):
    recorded = []

    def record(sender, template, context, **extra):
        recorded.append((template.name, context))

    template_rendered.connect(record, app)
    try:
        yield recorded
    finally:
        template_rendered.disconnect(record, app)

# Тесты для проверки шаблонов
def test_index_uses_correct_template(client, captured_templates):
    client.get('/')
    assert len(captured_templates) == 1
    template, context = captured_templates[0]
    assert template == 'index.html'

def test_posts_uses_correct_template(client, captured_templates):
    client.get('/posts')
    assert len(captured_templates) == 1
    template, context = captured_templates[0]
    assert template == 'posts.html'

def test_post_uses_correct_template(client, captured_templates):
    client.get('/posts/0')
    assert len(captured_templates) == 1
    template, context = captured_templates[0]
    assert template == 'post.html'

def test_about_uses_correct_template(client, captured_templates):
    client.get('/about')
    assert len(captured_templates) == 1
    template, context = captured_templates[0]
    assert template == 'about.html'

# Тесты для проверки передаваемых данных
def test_posts_template_gets_posts_data(client, captured_templates):
    client.get('/posts')
    template, context = captured_templates[0]
    assert 'posts' in context
    assert len(context['posts']) == 5
    assert 'title' in context
    assert context['title'] == 'Посты'

def test_post_template_gets_post_data(client, captured_templates):
    client.get('/posts/0')
    template, context = captured_templates[0]
    assert 'post' in context
    post = context['post']
    assert 'title' in post
    assert 'text' in post
    assert 'author' in post
    assert 'date' in post
    assert 'image_id' in post
    assert 'comments' in post

# Тесты для проверки отображения данных поста
def test_post_page_contains_all_data(client):
    # 1. Клиент УЖЕ создаёт контекст при get()
    response = client.get('/posts/0')  # Контекст создаётся автоматически
    assert response.status_code == 200
    
    # 2. Декодируем HTML-ответ
    post_data = response.data.decode('utf-8')
    
    # 3. Импортируем функцию НАПРЯМУЮ (без обращения к flask_app)
    
    
    # 4. Берём тестовые данные
    post = posts_list()[0]  # Первый пост
    
    # 5. Проверяем соответствие данных
    assert post['title'] in post_data  # Заголовок есть в HTML
    assert post['author'] in post_data  # Автор отображается
    assert post['text'] in post_data  # Основной текст
    
    # 6. Проверяем изображение (ID без .jpg)
    assert post['image_id'].split('.')[0] in post_data
    
    # 7. Проверяем комментарии
    for comment in post['comments']:
        assert comment['author'] in post_data  # Автор комментария
        assert comment['text'] in post_data  # Текст комментария
        for reply in comment.get('replies', []):  # Безопасная проверка replies
            assert reply['author'] in post_data
            assert reply['text'] in post_data

# Тесты для проверки формата даты
def test_post_date_format_in_list(client):
    # 1. Получаем список постов
    response = client.get('/posts')
    assert response.status_code == 200
    html_content = response.data.decode('utf-8')
    
    # 2. Берем дату первого поста из posts_list()
    post = posts_list()[0]
    expected_date = post['date'].strftime('%d.%m.%Y')
    
    # 3. Проверяем наличие даты в правильном формате
    assert expected_date in html_content

def test_post_date_format_in_single_page(client):
    # 1. Получаем страницу поста
    response = client.get('/posts/0')
    assert response.status_code == 200
    html_content = response.data.decode('utf-8')
    
    # 2. Берем дату первого поста из posts_list()
    post = posts_list()[0]
    expected_date = post['date'].strftime('%d.%m.%Y %H:%M')
    
    # 3. Проверяем наличие даты в правильном формате
    assert expected_date in html_content

# Тесты для обработки ошибок
def test_nonexistent_post_returns_404(client):
    response = client.get('/posts/999')
    assert response.status_code == 404

# Дополнительные тесты для полного покрытия
def test_base_template_elements(client):
    """Проверяем основные элементы шаблона"""
    response = client.get('/')
    html = response.data.decode('utf-8')
    assert 'navbar' in html
    assert 'footer' in html
    assert 'Лабораторная работа №1' in html

def test_comment_form_exists(client):
    """Проверяем наличие формы комментария"""
    response = client.get('/posts/0')
    html = response.data.decode('utf-8')
    assert 'Оставьте комментарий:' in html
    assert 'textarea' in html
    assert 'Отправить' in html

def test_posts_list_contains_all_posts(client):
    """Проверяем отображение всех постов в списке"""
    from app import posts_list  # Импортируем напрямую
    response = client.get('/posts')
    html = response.data.decode('utf-8')
    for post in posts_list():
        assert post['title'] in html
        assert post['author'] in html

def test_post_image_displayed(client):
    """Проверяем отображение изображения поста"""
    response = client.get('/posts/0')
    html = response.data.decode('utf-8')
    assert 'img-fluid rounded' in html
    assert 'src="/static/images/' in html

def test_about_page_content(client):
    """Проверяем содержание страницы 'Об авторе'"""
    response = client.get('/about')
    html = response.data.decode('utf-8')
    assert 'Об авторе' in html