# COF - Coffee & Tea Internet Shop

[![Django](https://img.shields.io/badge/Django-5.2.4-green.svg)](https://djangoproject.com/)
[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://python.org/)
[![Docker](https://img.shields.io/badge/Docker-Compose-blue.svg)](https://docker.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-17-blue.svg)](https://postgresql.org/)

## Description

Hi, everyone! It's my first PET-project.

This e-commerce project was created while learning how to work with the Django framework.
By examining the project code, you'll understand the principles of authentication, authorization, shopping cart, 
pagination, templates and views, order processing, using promo, and email notifications.

## 🚀 Features

- **Modern Architecture**: Django 5.2+ with type hints and comprehensive docstrings
- **Modular Apps**: Separate Django apps (catalog, cart, order, promo, users)
- **Containerization**: Full Docker configuration with PostgreSQL and Nginx
- **Performance**: Gunicorn with gevent, optimized database queries
- **Testing**: Comprehensive test coverage with pytest
- **Code Quality**: Ruff for linting and formatting

## 🛠️ Tech Stack

### Backend
- **Django 5.2.4** - web framework
- **Python 3.11+** (3.12 in Docker image) - programming language
- **PostgreSQL 17** - database
- **Gunicorn + Gevent** - WSGI server
- **Nginx** - web server and proxy

### Development Tools
- **uv** + **uv.lock** - dependency management and reproducible installs
- **Docker & Docker Compose** - containerization
- **pytest** - testing framework
- **Ruff** - linting and formatting
- **Django Extensions** - additional commands

## 📋 Requirements

- Python 3.11+
- Docker & Docker Compose
- uv (optional, for local development without Docker)

### Local Development (without Docker)

```bash
uv sync
cp .env.example .env
# Set DATABASE_HOST=localhost and ensure PostgreSQL is running
cd coffeeshop
python manage.py migrate
python manage.py runserver
```

## 🚀 Quick Start

### With Docker (Recommended)

1. **Clone the repository:**
```bash
git clone https://gitlab.com/srt-2000/cof.git
cd cof
```

2. **Configure environment variables:**
```bash
cp .env.example .env
# Edit .env if needed (email settings, passwords)
```

3. **Start the application:**
```bash
docker compose up --build
```

4. **Load test data (optional):**
```bash
docker compose exec coffeeshop python manage.py loadtestdata
```

The application will be available at: http://localhost

## 🔧 Configuration

### Environment Variables

Copy the example file and edit your local `.env` (do not commit it):

```bash
cp .env.example .env
```

Required variables are documented in `.env.example`. Example:

```env
# Django
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=127.0.0.1 localhost [::1]

# Database (use service name "postgres" for Docker Compose)
DATABASE_ENGINE=django.db.backends.postgresql
DATABASE_NAME=cof_db
DATABASE_USERNAME=postgres
DATABASE_PASSWORD=your-password
DATABASE_HOST=postgres
DATABASE_PORT=5432

# Tests (docker-compose.test.yml service name)
TEST_DATABASE_HOST=test-postgres

# Email
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
GMAIL_HOST_USER=your-email@gmail.com
GMAIL_APP_PASSWORD=your-app-password
ADMIN_EMAIL=admin@example.com
```

With Docker Compose, database migrations run automatically via the `coffeeshop-migrations` one-shot service before the app starts.

## 🧪 Testing & Code Quality

### Running Tests (Docker, recommended)

Runs format check, lint, migrations, and pytest against an isolated test database:

```bash
docker compose -f docker-compose.test.yml up --build --abort-on-container-exit --exit-code-from test test
```

`Aborting on container exit...` and container stop messages are expected when using `--abort-on-container-exit`.

### Running Tests Locally

Requires PostgreSQL and a configured `.env` (same variables as for the app; point `DATABASE_HOST` to your DB host, e.g. `localhost`):

```bash
uv sync --group dev
cd coffeeshop && python manage.py migrate && cd ..
pytest
```

### Code Linting & Formatting

Match the Docker test pipeline locally:

```bash
uv sync --group dev
ruff format --check .
ruff check .
```

Auto-fix:

```bash
ruff format .
ruff check --fix .
```

## 📁 Project Structure

```
coffeeshop/
├── catalog/                 # Product catalog
│   ├── models.py           # Product models
│   ├── views.py            # Catalog views
│   ├── filters.py          # Product filters
│   └── management/         # Django commands
├── cart/                   # Shopping cart
│   ├── cart.py            # Cart logic
│   ├── storage.py         # Cart storage
│   └── product_service.py  # Product service
├── order/                  # Orders
│   ├── models.py          # Order models
│   ├── services.py       # Business logic
│   └── forms.py           # Order forms
├── promo/                  # Promo codes
│   ├── models.py          # Promo models
│   ├── promo.py           # Promo logic
│   └── promo_factory.py   # Promo factory
├── users/                  # Users
│   ├── authentication.py  # Custom authentication
│   └── forms.py           # User forms
└── config/                # Django settings
    ├── settings.py        # Main settings
    ├── urls.py           # URL routes
    └── wsgi.py           # WSGI configuration
```

## 👨‍💻 Author

**srt-2000** - [srt2000888@gmail.ru](mailto:srt2000888@gmail.ru)

## 🔗 Useful Links

- [Django Documentation](https://docs.djangoproject.com/)
- [Docker Documentation](https://docs.docker.com/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [pytest Documentation](https://docs.pytest.org/)
