Нам потрібні 2 файли: app.py і test_app.py
Відкриваємо термінал, і вводимо наступне:
set FLASK_ENV='development'
set FLASK_APP=app.py
poetry run flask run

для того щоб запустити з WSGI-сервера потрібно у Git Bash виконати:
waitress-serve —port=8000 pplabs:app

Anaconda powershell:
створити і активувати середовище, потім:
pip install alembic
alembic init alembic
Потім:
change sqlalchemy.url in your alembic.ini file.
Для створення скриптів міграцій в новий файл alembic: 
alembic revision --autogenerate -m 'Initial script'
Для створення таблиць у базі даних:
alembic upgrade head
Щоб створити автоматично таблиці з бази даних в MySQL:
pip install sqlacodegen
