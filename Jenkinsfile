
pipeline {
    agent any

    options {
        timestamps()
        disableConcurrentBuilds()
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
                echo 'GitHub checkout completed'
            }
        }

        stage('Verify Project') {
            steps {
                bat '''
                    if not exist main.py exit /b 1
                    if not exist requirements.txt exit /b 1
                    if not exist Dockerfile exit /b 1
                    echo Project files verified
                '''
            }
        }

        stage('Docker Build') {
            steps {
                bat 'docker --version'
                bat 'docker build -t sentinel-ai:jenkins .'
            }
        }
    }

    post {
        success {
            echo 'Sentinel AI CI pipeline completed successfully!'
        }
        failure {
            echo 'Pipeline failed. Check Console Output.'
        }
    }
}
