
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
                echo 'GitHub checkout completed successfully'
            }
        }

        stage('Verify Project') {
            steps {
                bat '''
                    if not exist main.py exit /b 1
                    if not exist requirements.txt exit /b 1
                    if not exist Dockerfile exit /b 1
                    echo Project files verified successfully
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
                echo 'Building Sentinel AI Docker image...'

                bat '"%DOCKER_BIN%\\docker.exe" build -t sentinel-ai:jenkins .'

                echo 'Docker image build completed successfully'
            }
        }
    }

    post {
        success {
            echo 'SUCCESS: Sentinel AI CI/CD pipeline completed!'
        }

        failure {
            echo 'FAILED: Check Jenkins Console Output for errors.'
        }

        always {
            echo 'Jenkins pipeline execution finished.'
        }
    }
}
