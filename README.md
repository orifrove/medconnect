# MedConnect API

Backend API для системы записи пациентов к врачам.

## Технологии

- Python 3.12
- Django 6.0
- Django REST Framework
- PostgreSQL
- JWT Authentication
- Swagger UI

## Установка

```bash
git clone https://github.com/orifrove/medconnect.git
cd medconnect
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Создай `.env` файл:

```env
SECRET_KEY=your-secret-key
DEBUG=True
DB_NAME=medconnect_db
DB_USER=postgres
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432
ALLOWED_HOSTS=localhost,127.0.0.1
```

```bash
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

## Документация

После запуска открой: http://127.0.0.1:8000/api/docs/

## Эндпоинты

| Метод | URL | Описание |
|---|---|---|
| POST | /api/auth/register/doctor/ | Регистрация врача |
| POST | /api/auth/register/patient/ | Регистрация пациента |
| POST | /api/auth/login/ | Получить JWT токен |
| POST | /api/auth/refresh/ | Обновить токен |
| GET | /api/auth/me/ | Мой профиль |
| GET | /api/doctors/ | Список врачей |
| GET | /api/doctors/{id}/slots/ | Свободные слоты врача |
| GET/POST | /api/appointments/ | Записи на приём |
| POST | /api/appointments/{id}/cancel/ | Отменить запись |
| PATCH | /api/appointments/{id}/complete/ | Завершить приём |
| GET/POST | /api/medical-records/ | Медицинские карты |
| GET/POST | /api/reviews/ | Отзывы о враче |
| GET/POST | /api/messages/ | Сообщения |

## Автор

Shokirhodjaev Orif — [@orifrove](https://github.com/orifrove)
