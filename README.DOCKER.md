# Docker Setup Guide for SkyLearn

This guide explains how to run SkyLearn using Docker and Docker Compose.

## Prerequisites

- Docker (version 20.10 or higher)
- Docker Compose (version 2.0 or higher)

## Quick Start

### Development Environment

1. **Create a `.env` file** in the root directory with the following variables:

```env
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
DATABASE_URL=postgresql://skylearn_user:skylearn_password@db:5432/skylearn

# Email Configuration (optional)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
EMAIL_FROM_ADDRESS=your-email@gmail.com

# Stripe Configuration (optional)
STRIPE_SECRET_KEY=your-stripe-secret-key
STRIPE_PUBLISHABLE_KEY=your-stripe-publishable-key

# Student/Lecturer ID Prefixes
STUDENT_ID_PREFIX=ugr
LECTURER_ID_PREFIX=lec
```

2. **Build and run the containers**:

```bash
docker-compose up --build
```

3. **Create a superuser** (in a new terminal):

```bash
docker-compose exec web python manage.py createsuperuser
```

4. **Access the application**:

- Application: http://localhost:8000
- Admin panel: http://localhost:8000/admin

### Production Environment

1. **Update your `.env` file** with production settings:

```env
SECRET_KEY=your-strong-secret-key-here
DEBUG=False
ALLOWED_HOSTS=your-domain.com,www.your-domain.com
DATABASE_URL=postgresql://skylearn_user:skylearn_password@db:5432/skylearn
```

2. **Build and run with production configuration**:

```bash
docker-compose -f docker-compose.prod.yml up --build -d
```

3. **Create a superuser**:

```bash
docker-compose -f docker-compose.prod.yml exec web python manage.py createsuperuser
```

## Common Commands

### View logs
```bash
docker-compose logs -f web
```

### Run migrations
```bash
docker-compose exec web python manage.py migrate
```

### Create superuser
```bash
docker-compose exec web python manage.py createsuperuser
```

### Access Django shell
```bash
docker-compose exec web python manage.py shell
```

### Stop containers
```bash
docker-compose down
```

### Stop and remove volumes (WARNING: This deletes database data)
```bash
docker-compose down -v
```

### Rebuild containers
```bash
docker-compose up --build
```

## Database

The default setup uses PostgreSQL. The database data is persisted in a Docker volume named `postgres_data`.

To backup the database:
```bash
docker-compose exec db pg_dump -U skylearn_user skylearn > backup.sql
```

To restore the database:
```bash
docker-compose exec -T db psql -U skylearn_user skylearn < backup.sql
```

## Troubleshooting

### Port already in use
If port 8000 is already in use, modify the port mapping in `docker-compose.yml`:
```yaml
ports:
  - "8001:8000"  # Change 8001 to any available port
```

### Database connection errors
Ensure the database container is healthy:
```bash
docker-compose ps
```

### Static files not loading
Run collectstatic:
```bash
docker-compose exec web python manage.py collectstatic --noinput
```

