# run.py

# 1. Сначала импортируем фабрику и команду
from app import create_app
from init_db import init_db_command

# 2. Затем создаем экземпляр приложения
app = create_app()

# 3. И СРАЗУ ПОСЛЕ ЭТОГО регистрируем команду
app.cli.add_command(init_db_command)

# Этот блок if __name__ ... выполняется только при запуске 'python run.py',
# а не 'flask run', поэтому он не имеет значения для CLI.
if __name__ == '__main__':
    app.run(debug=True)