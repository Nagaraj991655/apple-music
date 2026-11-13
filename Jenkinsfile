
pipeline {
    agent any

    options {
        timestamps()
        disableConcurrentBuilds()
        skipDefaultCheckout(true)
    }

    environment {
        COMPOSE_PROJECT_NAME = 'apple-music'
    }

    stages {
        stage('Checkout') {
            steps {
                echo 'Checking out source code from GitHub'
                checkout scm
                sh 'git log -1 --oneline'
            }
        }

        stage('Validate') {
            steps {
                echo 'Validating Docker Compose configuration'
                sh '''
                    set -eu
                    docker --version
                    docker compose version
                    docker compose config -q
                '''
            }
        }

        stage('Build') {
            steps {
                echo 'Building Docker images'
                sh '''
                    set -eu
                    docker compose build
                '''
            }
        }

        stage('Deploy') {
            steps {
                echo 'Deploying application'
                sh '''
                    set -eu
                    docker compose up -d --remove-orphans
                    docker compose ps
                '''
            }
        }

        stage('Verify') {
            steps {
                echo 'Checking application'
                sh '''
                    set -eu
                    for i in $(seq 1 30); do
                        if curl -fsS http://localhost/ > /dev/null; then
                            echo "Application is running successfully"
                            exit 0
                        fi
                        sleep 5
                    done

                    echo "Application health check failed"
                    docker compose logs --tail=100
                    exit 1
                '''
            }
        }
    }

    post {
        success {
            echo 'APPLE MUSIC DEPLOYMENT SUCCESSFUL'
            echo 'Application: http://204.236.243.177'
        }

        failure {
            echo 'PIPELINE FAILED - Check Console Output'
            sh 'docker compose logs --tail=100 || true'
        }
    }
}
