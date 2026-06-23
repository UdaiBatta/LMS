# CI/CD Setup Guide for SkyLearn

This guide explains how to set up Continuous Integration and Continuous Deployment for SkyLearn using Bitbucket Pipelines and Jenkins.

## Bitbucket Pipelines

### Setup Instructions

1. **Enable Pipelines** in your Bitbucket repository:
   - Go to Repository Settings → Pipelines → Settings
   - Enable Pipelines

2. **Configure Repository Variables** (Repository Settings → Pipelines → Repository variables):
   - `DOCKER_REGISTRY` (optional): Your Docker registry URL
   - `DOCKER_USERNAME` (optional): Docker registry username
   - `DOCKER_PASSWORD` (optional): Docker registry password (mark as secured)

3. **Branch Strategy**:
   - `main` branch: Deploys to production
   - `develop` branch: Deploys to staging
   - Pull requests: Runs tests only

### Pipeline Workflows

- **Default**: Runs tests and builds Docker image
- **Pull Requests**: Runs tests only
- **Develop Branch**: Runs tests, builds image, and deploys to staging
- **Main Branch**: Runs tests, builds image, and deploys to production

### Customizing Deployment

Edit `bitbucket-pipelines.yml` to add your deployment steps:

```yaml
- step: &deploy-production
    name: Deploy to Production
    deployment: production
    script:
      - docker build -t skylearn:production .
      - docker push your-registry/skylearn:production
      - ssh user@server "docker pull your-registry/skylearn:production && docker-compose up -d"
```

## Jenkins

### Setup Instructions

1. **Install Required Plugins**:
   - Docker Pipeline
   - Git
   - JUnit (for test reports)

2. **Configure Jenkins**:
   - Go to Manage Jenkins → Configure System
   - Ensure Docker is installed and accessible
   - Configure Git credentials if needed

3. **Create a New Pipeline Job**:
   - New Item → Pipeline
   - Configure → Pipeline → Definition: Pipeline script from SCM
   - SCM: Git
   - Repository URL: Your repository URL
   - Script Path: `Jenkinsfile`

4. **Configure Credentials** (if needed):
   - Add Docker registry credentials
   - Add SSH credentials for deployment

### Pipeline Stages

1. **Checkout**: Clones the repository
2. **Setup Python Environment**: Verifies Python installation
3. **Install Dependencies**: Installs Python packages
4. **Code Quality Check**: Runs Django checks
5. **Run Tests**: Executes test suite
6. **Collect Static Files**: Prepares static files
7. **Build Docker Image**: Creates Docker image
8. **Docker Image Tagging**: Tags the image

### Customizing Deployment

Edit the `post` section in `Jenkinsfile` to add deployment steps:

```groovy
post {
    success {
        script {
            if (env.BRANCH_NAME == 'main') {
                sh 'docker push your-registry/skylearn:${DOCKER_TAG}'
                sh 'ssh user@server "docker pull your-registry/skylearn:${DOCKER_TAG} && docker-compose -f docker-compose.prod.yml up -d"'
            }
        }
    }
}
```

## Environment Variables

Both CI/CD systems may need access to environment variables. Configure them in:

- **Bitbucket**: Repository Settings → Pipelines → Repository variables
- **Jenkins**: Pipeline job → Configure → Build Environment → Use secret text(s) or file(s)

Common variables:
- `SECRET_KEY`
- `DATABASE_URL`
- `EMAIL_HOST_USER`
- `EMAIL_HOST_PASSWORD`
- `STRIPE_SECRET_KEY`
- `STRIPE_PUBLISHABLE_KEY`

## Best Practices

1. **Never commit secrets**: Use environment variables or secret management
2. **Test locally first**: Run tests before pushing
3. **Use feature branches**: Create PRs for code review
4. **Monitor builds**: Set up notifications for build failures
5. **Version tags**: Tag releases in Git for traceability

## Troubleshooting

### Bitbucket Pipelines

- **Build fails**: Check logs in Pipelines → Builds
- **Docker build fails**: Ensure Docker service is enabled in pipeline
- **Tests fail**: Review test output in build logs

### Jenkins

- **Pipeline not running**: Check SCM configuration
- **Docker commands fail**: Ensure Docker is installed and Jenkins user has permissions
- **Tests fail**: Review console output for details

