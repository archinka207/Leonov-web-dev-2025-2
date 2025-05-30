import re
from flask import Flask, request, render_template, make_response, redirect, url_for

app = Flask(__name__)

# Маршрут для главной страницы, перенаправляет на заголовки
@app.route('/')
def index():
    return redirect(url_for('headers'))

@app.route('/url')
def url():
    # request.args - это ImmutableMultiDict, содержащий параметры запроса
    url_params = request.args.items()
    return render_template('url.html', title='Параметры URL', url_params=url_params)

@app.route('/headers')
def headers():
    # request.headers - это Headers (наследник dict), содержащий заголовки запроса
    request_headers = request.headers.items()
    return render_template('headers.html', title='Заголовки запроса', request_headers=request_headers)

@app.route('/cookies')
def cookies():
    cookie_name = 'my_cookie'
    cookie_value = 'flask_value'
    
    # Создаем объект ответа
    response = make_response(render_template('cookies.html', title='Куки'))

    # Проверяем, установлено ли куки
    if cookie_name in request.cookies:
        # Если куки установлено, удаляем его
        response.delete_cookie(cookie_name)
        response.set_data(render_template('cookies.html', title='Куки', cookie_status='удалено'))
    else:
        # Если куки не установлено, устанавливаем его
        response.set_cookie(cookie_name, cookie_value, max_age=60*60*24*7) # Куки на 7 дней
        response.set_data(render_template('cookies.html', title='Куки', cookie_status='установлено'))
    
    return response

@app.route('/form', methods=['GET', 'POST'])
def form():
    form_data = None
    if request.method == 'POST':
        # request.form - это ImmutableMultiDict, содержащий данные формы
        form_data = request.form.items()
    return render_template('form.html', title='Параметры формы', form_data=form_data)

@app.route('/phone', methods=['GET', 'POST'])
def phone():
    phone_number = ""
    formatted_phone = ""
    error_message = ""
    is_invalid = False

    if request.method == 'POST':
        phone_number = request.form.get('phone_number', '').strip()
        
        # Шаг 1: Удаляем разрешенные дополнительные символы
        # Разрешенные символы: пробелы, круглые скобки, дефисы, точки, +
        cleaned_number = re.sub(r'[()\s\-\.]', '', phone_number)

        # Шаг 2: Проверяем на недопустимые символы (остались ли что-то кроме цифр и '+')
        if not re.fullmatch(r'\+?\d+', cleaned_number):
            error_message = "Недопустимый ввод. В номере телефона встречаются недопустимые символы."
            is_invalid = True
        else:
            # Шаг 3: Проверяем длину и префиксы
            digits_only = re.sub(r'\D', '', phone_number) # Получаем только цифры для проверки длины

            # Если номер начинается с '+7' или '8', он должен содержать 11 цифр
            if phone_number.startswith('+7') or phone_number.startswith('8'):
                if len(digits_only) != 11:
                    error_message = "Недопустимый ввод. Неверное количество цифр." \
                                    " (Номер должен содержать 11 цифр, если начинается с '+7' или '8')"
                    is_invalid = True
            # В остальных случаях (без префикса или с другим префиксом), 10 цифр
            else:
                if len(digits_only) != 10:
                    error_message = "Недопустимый ввод. Неверное количество цифр." \
                                    " (Номер должен содержать 10 цифр)"
                    is_invalid = True
            
            # Если ошибок нет, форматируем номер
            if not is_invalid:
                # Приводим к 11-значному формату для форматирования
                if len(digits_only) == 10:
                    # Если 10 цифр, считаем, что это российский номер без 8/7
                    digits_only = '8' + digits_only
                elif phone_number.startswith('+7'):
                    digits_only = '8' + digits_only[1:] # Заменяем +7 на 8
                
                # Форматирование в 8-***-***-**-**
                if len(digits_only) == 11:
                    formatted_phone = f"8-{digits_only[1:4]}-{digits_only[4:7]}-{digits_only[7:9]}-{digits_only[9:11]}"
                else:
                    # Это запасной случай, если вдруг пропустили ошибку длины
                    error_message = "Недопустимый ввод. Неверное количество цифр."
                    is_invalid = True

    return render_template('phone.html', 
                           title='Валидация номера телефона',
                           phone_number=phone_number,
                           formatted_phone=formatted_phone,
                           error_message=error_message,
                           is_invalid=is_invalid)

if __name__ == '__main__':
    app.run(debug=True)
