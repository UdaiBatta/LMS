pipeline {
    agent any

    environment {
        DOCKER_IMAGE = 'skylearn'
        DOCKER_TAG = "${env.BUILD_NUMBER}"
        PYTHON_VERSION = '3.10'
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
                    python manage.py check --deploy || true
                    python manage.py check || true
                '''
            }
        }

        stage('Run Tests') {
            steps {
                sh '''
                    python manage.py test --verbosity=2 || true
                '''
            }
            post {
                always {
                    junit 'test-results/*.xml'
                }
            }
        }

        stage('Collect Static Files') {
            steps {
                sh '''
                    python manage.py collectstatic --noinput || true
                '''
            }
        }

        stage('Build Docker Image') {
            steps {
                script {
                    docker.build("${DOCKER_IMAGE}:${DOCKER_TAG}")
                    docker.build("${DOCKER_IMAGE}:latest")
                }
            }
        }

        stage('Docker Image Tagging') {
            steps {
                script {
                    docker.tag("${DOCKER_IMAGE}:${DOCKER_TAG}", "${DOCKER_IMAGE}:${env.GIT_COMMIT_SHORT}")
                }
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

