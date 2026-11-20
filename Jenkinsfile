
pipeline {
    agent any

    environment {
        DOCKER_BIN = 'C:\\Users\\cpulk\\AppData\\Local\\Programs\\DockerDesktop\\resources\\bin'
        PYTHON_EXE = 'C:\\Users\\cpulk\\AppData\\Local\\Python\\pythoncore-3.12-64\\python.exe'
    }

    options {
        timestamps()
        disableConcurrentBuilds()
        skipDefaultCheckout(true)
    }

    stages {

        stage('Checkout') {
            steps {
                checkout scm
                echo 'SUCCESS: GitHub checkout completed'
            }
        }

        stage('Verify Project') {
            steps {
                bat '''
                    @echo off

                    if not exist main.py exit /b 1
                    if not exist requirements.txt exit /b 1
                    if not exist requirements-dev.txt exit /b 1
                    if not exist Dockerfile exit /b 1
                    if not exist tests\\test_api.py exit /b 1

                    echo SUCCESS: Project files verified
                '''
            }
        }

        stage('Check Python') {
            steps {
                bat '''
                    @echo off

                    if not exist "%PYTHON_EXE%" (
                        echo ERROR: Python executable not found
                        exit /b 1
                    )

                    "%PYTHON_EXE%" --version
                    if errorlevel 1 exit /b 1

                    echo SUCCESS: Python verified
                '''
            }
        }

        stage('Run Automated Tests') {
            steps {
                bat '''
                    @echo off

                    echo Creating Python virtual environment...

                    "%PYTHON_EXE%" -m venv .jenkins-venv
                    if errorlevel 1 exit /b 1

                    echo Installing testing dependencies...

                    ".jenkins-venv\\Scripts\\python.exe" -m pip install -r requirements-dev.txt
                    if errorlevel 1 exit /b 1

                    echo Running automated pytest tests...

                    ".jenkins-venv\\Scripts\\python.exe" -m pytest -v tests
                    if errorlevel 1 exit /b 1

                    echo SUCCESS: Automated tests passed
                '''
            }
        }

        stage('Check Docker') {
            steps {
                bat '''
                    @echo off

                    "%DOCKER_BIN%\\docker.exe" --version
                    if errorlevel 1 exit /b 1

                    "%DOCKER_BIN%\\docker.exe" info
                    if errorlevel 1 exit /b 1

                    echo SUCCESS: Docker verified
                '''
            }
        }

        stage('Docker Build') {
            steps {
                echo 'Building Sentinel AI Docker image...'

                bat '''
                    @echo off

                    "%DOCKER_BIN%\\docker.exe" build -t sentinel-ai:jenkins .
                    if errorlevel 1 exit /b 1

                    echo SUCCESS: Docker image built
                '''
            }
        }
    }

    post {
        success {
            echo 'SUCCESS: Sentinel AI CI/CD pipeline completed!'
            echo 'All automated tests passed and Docker image built.'
        }

        failure {
            echo 'FAILED: Check Jenkins Console Output for errors.'
        }

        always {
            echo 'Jenkins pipeline execution finished.'
        }
    }
}
