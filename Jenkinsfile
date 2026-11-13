
pipeline {
    agent any

    options {
        timestamps()
        disableConcurrentBuilds()
    }

    environment {
        EC2_HOST = '204.236.243.177'
        DEPLOY_DIR = '/home/ubuntu/apple-music'
        BRANCH = 'main'
    }

    stages {

        stage('Checkout') {
            steps {
                echo 'Checking out source code from GitHub'
                checkout scm
            }
        }

        stage('Validate') {
            steps {
                echo 'Validating Docker Compose configuration'
                withCredentials([
                    sshUserPrivateKey(
                        credentialsId: 'ec2-ssh-key',
                        keyFileVariable: 'SSH_KEY',
                        usernameVariable: 'SSH_USER'
                    )
                ]) {
                    sh '''
                        ssh -i "$SSH_KEY" \
                            -o BatchMode=yes \
                            -o StrictHostKeyChecking=accept-new \
                            "$SSH_USER@$EC2_HOST" \
                            "cd $DEPLOY_DIR && docker compose config -q"
                    '''
                }
            }
        }

        stage('Deploy to EC2') {
            steps {
                echo 'Deploying Apple Music application'

                withCredentials([
                    sshUserPrivateKey(
                        credentialsId: 'ec2-ssh-key',
                        keyFileVariable: 'SSH_KEY',
                        usernameVariable: 'SSH_USER'
                    )
                ]) {
                    sh '''
                        ssh -i "$SSH_KEY" \
                            -o BatchMode=yes \
                            -o StrictHostKeyChecking=accept-new \
                            "$SSH_USER@$EC2_HOST" \
                            "cd $DEPLOY_DIR &&
                             git pull --ff-only origin $BRANCH &&
                             docker compose build &&
                             docker compose up -d &&
                             docker compose ps"
                    '''
                }
            }
        }
    }

    post {
        success {
            echo 'Apple Music application deployed successfully!'
        }

        failure {
            echo 'Pipeline failed. Check the Jenkins console output.'
        }
    }
}
