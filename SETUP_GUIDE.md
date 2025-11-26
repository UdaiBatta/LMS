# SkyLearn - Docker, Bitbucket & Jenkins Setup Guide

This document provides a comprehensive guide for setting up Docker, Bitbucket Pipelines, and Jenkins for the SkyLearn project.

## 📦 Docker Setup

### Files Created
- `Dockerfile` - Development Docker image
- `Dockerfile.prod` - Production Docker image with Gunicorn
- `docker-compose.yml` - Development multi-container setup
- `docker-compose.prod.yml` - Production multi-container setup
- `.dockerignore` - Files to exclude from Docker builds
- `README.DOCKER.md` - Detailed Docker documentation

### Quick Start

1. **Create `.env` file** (copy from `.env.example` if available):
```env
SECRET_KEY=your-secret-key
DEBUG=True
DATABASE_URL=postgresql://skylearn_user:skylearn_password@db:5432/skylearn
```

2. **Start development environment**:
```bash
docker-compose up --build
```

3. **Create superuser**:
```bash
docker-compose exec web python manage.py createsuperuser
```

4. **Access application**: http://localhost:8000

### Production Deployment
```bash
docker-compose -f docker-compose.prod.yml up --build -d
```

## 🔄 Bitbucket Pipelines

### Files Created
- `bitbucket-pipelines.yml` - CI/CD pipeline configuration

### Setup Steps

1. **Enable Pipelines**:
   - Repository Settings → Pipelines → Settings
   - Enable Pipelines

2. **Configure Variables** (Repository Settings → Pipelines → Repository variables):
   - Add any required environment variables
   - Mark sensitive values as "Secured"

3. **Pipeline Workflows**:
   - **Default**: Tests + Docker build
   - **Pull Requests**: Tests only
   - **develop branch**: Tests + Build + Staging deployment
   - **main branch**: Tests + Build + Production deployment

### Customizing Deployment

Edit `bitbucket-pipelines.yml` to add your deployment commands in the `deploy-staging` and `deploy-production` steps.

## 🔧 Jenkins Setup

### Files Created
- `Jenkinsfile` - Declarative pipeline configuration

### Setup Steps

1. **Install Plugins**:
   - Docker Pipeline
   - Git
   - JUnit

2. **Create Pipeline Job**:
   - New Item → Pipeline
   - Pipeline → Definition: Pipeline script from SCM
   - SCM: Git
   - Repository URL: Your repository URL
   - Script Path: `Jenkinsfile`

3. **Configure Credentials** (if needed):
   - Docker registry credentials
   - SSH credentials for deployment

### Pipeline Stages

1. Checkout code
2. Setup Python environment
3. Install dependencies
4. Code quality checks
5. Run tests
6. Collect static files
7. Build Docker image
8. Tag Docker image

### Customizing Deployment

Edit the `post` section in `Jenkinsfile` to add deployment steps for production builds.

## 🔐 Environment Variables

Required environment variables (configure in respective platforms):

- `SECRET_KEY` - Django secret key
- `DEBUG` - Debug mode (False for production)
- `ALLOWED_HOSTS` - Comma-separated list of allowed hosts
- `DATABASE_URL` - PostgreSQL connection string (for Docker)
- `EMAIL_HOST_USER` - Email username
- `EMAIL_HOST_PASSWORD` - Email password
- `STRIPE_SECRET_KEY` - Stripe secret key (optional)
- `STRIPE_PUBLISHABLE_KEY` - Stripe publishable key (optional)

## 📝 Configuration Changes Made

1. **Updated `config/settings.py`**:
   - Added PostgreSQL support via `DATABASE_URL`
   - Removed test email code
   - Maintains backward compatibility with SQLite

2. **Updated `requirements/base.txt`**:
   - Added `psycopg2-binary` for PostgreSQL
   - Added `dj-database-url` for database URL parsing

## 🚀 Next Steps

1. **Docker**:
   - Review and customize `docker-compose.yml` for your needs
   - Update `.env` file with your actual values
   - Test locally with `docker-compose up`

2. **Bitbucket**:
   - Enable Pipelines in repository settings
   - Add repository variables
   - Customize deployment steps in `bitbucket-pipelines.yml`
   - Push to trigger first pipeline

3. **Jenkins**:
   - Install required plugins
   - Create pipeline job
   - Configure credentials
   - Customize `Jenkinsfile` for your deployment needs
   - Run first build

## 📚 Additional Documentation

- `README.DOCKER.md` - Detailed Docker usage guide
- `README.CI_CD.md` - Detailed CI/CD setup guide

## ⚠️ Important Notes

- Never commit `.env` file (already in `.gitignore`)
- Use strong `SECRET_KEY` in production
- Set `DEBUG=False` in production
- Configure proper `ALLOWED_HOSTS` for production
- Use secure passwords for database in production
- Review and customize deployment steps for your infrastructure

## 🆘 Troubleshooting

### Docker
- Check logs: `docker-compose logs -f web`
- Rebuild: `docker-compose up --build`
- Reset database: `docker-compose down -v`

### Bitbucket Pipelines
- Check build logs in Pipelines → Builds
- Verify repository variables are set
- Ensure Docker service is enabled

### Jenkins
- Check console output for errors
- Verify Docker is accessible
- Check credentials configuration
- Review pipeline logs

## 📞 Support

For issues or questions:
1. Check the detailed documentation files
2. Review error logs
3. Verify environment variables
4. Ensure all dependencies are installed

