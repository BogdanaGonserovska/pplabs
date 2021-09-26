Нам потрібні 2 файли: app.py і test_app.py

Відкриваємо термінал, і вводимо наступне:


set FLASK_ENV='development'

set FLASK_APP=app.py

poetry run flask run



Для того щоб запустити з WSGI-сервера потрібно у Git Bash виконати:

waitress-serve —port=8000 pplabs:app
