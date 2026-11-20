
pipeline {
    agent any

    environment {
        DOCKER_BIN = 'C:\\Users\\cpulk\\AppData\\Local\\Programs\\DockerDesktop\\resources\\bin'
    }

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
                    if not exist requirements-dev.txt exit /b 1
                    if not exist Dockerfile exit /b 1
                    if not exist tests\\test_api.py exit /b 1
                    echo Project files verified
                '''
            }
        }

        stage('Run Automated Tests') {
            steps {
                bat '''
                    py -3.12 -m venv .jenkins-venv
                    call .jenkins-venv\\Scripts\\python.exe -m pip install -r requirements-dev.txt
                    call .jenkins-venv\\Scripts\\python.exe -m pytest -v tests
                '''
            }
        }

        stage('Check Docker') {
            steps {
                bat '"%DOCKER_BIN%\\docker.exe" --version'
                bat '"%DOCKER_BIN%\\docker.exe" info'
            }
        }

        stage('Docker Build') {
            steps {
                bat '"%DOCKER_BIN%\\docker.exe" build -t sentinel-ai:jenkins .'
            }
        }
    }

    post {
        success {
            echo 'SUCCESS: Sentinel AI tests passed and Docker image built!'
        }
        failure {
            echo 'FAILED: Check Jenkins Console Output.'
        }
        always {
            echo 'Jenkins pipeline finished.'
        }
    }
}
