# COF - Coffee & Tea Internet Shop

[![Django](https://img.shields.io/badge/Django-5.2.4-green.svg)](https://djangoproject.com/)
[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://python.org/)
[![Docker](https://img.shields.io/badge/Docker-Compose-blue.svg)](https://docker.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-17-blue.svg)](https://postgresql.org/)

## Description

This e-commerce project was created while learning how to work with the Django framework.

##
By examining the project code, you'll understand the principles of authentication, authorization, shopping cart, 
pagination, templates and views, order processing, using promo, and email notifications.

## 🚀 Features

- **Modern Architecture**: Django 5.2+ with type hints and comprehensive docstrings
- **Microservice Structure**: Modular applications (catalog, cart, order, promo, users)
- **Containerization**: Full Docker configuration with PostgreSQL and Nginx
- **Security**: CSRF protection, data validation, secure cookies
- **Performance**: Gunicorn with gevent, optimized database queries
- **Testing**: Comprehensive test coverage with pytest
- **Code Quality**: Ruff for linting and formatting

## 🛠️ Tech Stack

### Backend
- **Django 5.2.4** - web framework
- **Python 3.11+** - programming language
- **PostgreSQL 17** - database
- **Gunicorn + Gevent** - WSGI server
- **Nginx** - web server and proxy

### Development Tools
- **Poetry** - dependency management
- **Docker & Docker Compose** - containerization
- **pytest** - testing framework
- **Ruff** - linting and formatting
- **Django Extensions** - additional commands

## 📋 Requirements

- Python 3.11+
- Docker & Docker Compose
- Poetry (optional)

## 🚀 Quick Start

### With Docker (Recommended)

1. **Clone the repository:**
```bash
git clone https://gitlab.com/srt-2000/cof.git
cd cof
```

2. **Configure environment variables:**
```bash
# Edit the .example file with your configuration values
nano .example

# After editing, rename the file to .env
mv .example .env
```

3. **For local development, configure the following:**

**In `.env` file:**
```env
ALLOWED_HOSTS=127.0.0.1 localhost [::1]
DEBUG=True
```

**In `nginx/coffeeshop_nginx.conf`, comment out lines 8, 9, 10, 18, 19, 20:**
```nginx
# location /.well-known/acme-challenge/ {
#     root /var/www/certbot;
# }

# server {
#     listen 443 ssl;
#     ssl_certificate /etc/letsencrypt/live/srt-tester.ru/fullchain.pem;
#     ssl_certificate_key /etc/letsencrypt/live/srt-tester.ru/privkey.pem;
```

**In `docker-compose.yml`, comment out lines 83-90:**
```yaml
# certbot:
#   image: certbot/certbot
#   volumes:
#     - ./certbot/conf:/etc/letsencrypt
#     - ./certbot/www:/var/www/certbot
#   command: certonly --webroot --webroot-path=/var/www/certbot/ --email srt2000888tester@gmail.com --agree-tos --no-eff-email -d srt-tester.ru
#   depends_on:
#     - nginx
```

4. **Start the application:**
```bash
docker-compose up -d
```

5. **Load test data:**
```bash
docker-compose exec coffeeshop python manage.py loadtestdata
```

The application will be available at: http://localhost

### Local Development

1. **Install dependencies:**
```bash
poetry install
poetry shell
```

2. **Set up database:**
```bash
# Create PostgreSQL database
createdb cof_db

# Run migrations
python manage.py migrate

# Load test data
python manage.py loadtestdata
```

3. **Start development server:**
```bash
python manage.py runserver
```

## 🔧 Configuration

### Environment Variables

The project includes a `.example` file with all required environment variables. You need to:

1. **Edit the `.example` file** with your configuration values
2. **Rename it to `.env`** after configuration

Example configuration:
```env
# Django
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=127.0.0.1 localhost [::1]

# Database
DATABASE_ENGINE=django.db.backends.postgresql
DATABASE_NAME=cof_db
DATABASE_USERNAME=postgres
DATABASE_PASSWORD=your-password
DATABASE_HOST=localhost
DATABASE_PORT=5432

# Email
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
GMAIL_HOST_USER=your-email@gmail.com
GMAIL_APP_PASSWORD=your-app-password
ADMIN_EMAIL=admin@example.com
```

## 🧪 Testing & Code Quality

### Running Tests
```bash
# Run tests with Docker
docker-compose -f docker-compose.test.yml up test-coffeeshop

# Run tests locally
pytest

# Run tests with coverage
pytest --cov=coffeeshop
```

### Code Linting
```bash
# Run linting with Docker
docker-compose -f docker-compose.test.yml up test-coffeeshop-lint

# Run linting locally
ruff check .
ruff format .
```

## 📊 Database Structure

### Core Models

- **Product** - products with categories, types, regions
- **Order** - orders with item details
- **Promo** - promo codes and discounts
- **User** - users with extended authentication

### Relationships
- Products linked to categories, types, regions, manufacturers
- Orders contain item details
- Promo codes can be applied to cart or products

## 🚀 Deployment

### Production Settings

1. **Configure environment variables for production**
2. **Start the application:**
```bash
docker-compose up -d
```

3. **Configure SSL certificates (optional):**
```bash
# Uncomment certbot in docker-compose.yml
docker-compose up -d nginx
docker-compose run --rm certbot certonly --webroot --webroot-path=/var/www/certbot/ -d your-domain.com
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