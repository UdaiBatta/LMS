pipeline {
    agent any

    environment {
        DOCKER_IMAGE = 'skylearn'
        DOCKER_TAG = "${env.BUILD_NUMBER}"
        PYTHON_VERSION = '3.10'
        SECRET_KEY = 'ci-only-secret-key-with-more-than-fifty-random-looking-characters'
        DEBUG = 'True'
        EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'
        EMAIL_HOST_USER = ''
        EMAIL_HOST_PASSWORD = ''
        EMAIL_FROM_ADDRESS = 'ci@example.com'
    }

    options {
        buildDiscarder(logRotator(numToKeepStr: '10'))
        timeout(time: 30, unit: 'MINUTES')
        timestamps()
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
                script {
                    env.GIT_COMMIT_SHORT = sh(
                        script: 'git rev-parse --short HEAD',
                        returnStdout: true
                    ).trim()
                }
            }
        }

        stage('Setup Python Environment') {
            steps {
                sh '''
                    python3 --version
                    pip3 --version
                '''
            }
        }

        stage('Install Dependencies') {
            steps {
                sh '''
                    pip3 install --upgrade pip
                    pip3 install -r requirements.txt
                '''
            }
        }

        stage('Code Quality Check') {
            steps {
                sh '''
                    python manage.py check
                    python manage.py makemigrations --check --dry-run
                '''
            }
        }

        stage('Run Tests') {
            steps {
                sh '''
                    python manage.py test --verbosity=2
                '''
            }
        }

        stage('Collect Static Files') {
            steps {
                sh '''
                    python manage.py collectstatic --noinput
                '''
            }
        }

        stage('Build Docker Image') {
            steps {
                script {
                    docker.build("${DOCKER_IMAGE}:${DOCKER_TAG}")
                }
                sh "docker tag ${DOCKER_IMAGE}:${DOCKER_TAG} ${DOCKER_IMAGE}:latest"
            }
        }

        stage('Docker Image Tagging') {
            steps {
                sh "docker tag ${DOCKER_IMAGE}:${DOCKER_TAG} ${DOCKER_IMAGE}:${GIT_COMMIT_SHORT}"
            }
        }
    }

    post {
        success {
            echo 'Pipeline succeeded!'
            script {
                if (env.BRANCH_NAME == 'main' || env.BRANCH_NAME == 'master') {
                    echo 'Production build completed successfully'
                    // Add deployment steps here
                }
            }
        }
        failure {
            echo 'Pipeline failed!'
            // Add notification steps here (email, Slack, etc.)
        }
        always {
            cleanWs()
        }
    }
}

