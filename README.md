[![Main Foodgram workflow](https://github.com/DankovaAlina/foodgram-project-react/actions/workflows/main.yml/badge.svg)](https://github.com/DankovaAlina/foodgram-project-react/actions/workflows/main.yml)

# **Описание проекта**

Cервис обмена рецептами.
Сервис поддерживает добавление новых рецептов от лица пользователя с фотографией и описанием, подписку на понравившихся авторов, добавление рецептов в избранное и список покупок, а также скачивание списка покупок.

Проект поддерживает развертку в Docker-контейнерах.

# **Стек технологий**

- Python 3.9.6
- Django 3.2.3
- Django REST Framework 3.12.4

# **Как запустить проект локально**

### **Клонировать репозиторий и перейти в него в командной строке:**

```
git clone https://github.com/DankovaAlina/foodgram-project-react.git
cd foodgram_project_react
```

### **Cоздать и активировать виртуальное окружение:**

```
python3 -m venv env
source env/bin/activate
```

### **Установить зависимости из файла requirements.txt:**

```
python3 -m pip install --upgrade pip
cd backend
pip install -r requirements.txt
```

### **Выполнить миграции:**

```
python3 manage.py migrate
```

### **Заполнить базу данных:**

```
python3 manage.py add_db_csv
```

### **Запустить проект:**

```
python3 manage.py runserver
```

# **Структура файла .env**

- USE_POSTGRES - bool - флаг использования PostgreSQL или SQLite
- POSTGRES_USER - str - логин пользователя в PostgreSQL
- POSTGRES_PASSWORD - str - пароль пользователя в PostgreSQL
- POSTGRES_DB - str - название БД в PostgreSQL
- DB_HOST - str - название хоста в PostgreSQL
- DB_PORT - int - порт PostgreSQL
- SECRET_KEY - str - ключ шифрования
- DEBUG - bool - флаг использования режима отладки
- ALLOWED_HOSTS - str - разрешенные хосты с разделителем через запятую ('localhost,127.0.0.1')

# **Автор**

@DankovaAlina
