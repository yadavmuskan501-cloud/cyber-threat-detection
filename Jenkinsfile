
pipeline {
    agent any

    environment {
        DOCKER_BIN = 'C:\\Users\\cpulk\\AppData\\Local\\Programs\\DockerDesktop\\resources\\bin'
        PYTHON_EXE = 'C:\\Users\\cpulk\\AppData\\Local\\Python\\pythoncore-3.12-64\\python.exe'
        HEADLESS = '1'
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
                    if not exist login.html exit /b 1
                    if not exist dashboard.html exit /b 1
                    if not exist requirements.txt exit /b 1
                    if not exist requirements-dev.txt exit /b 1
                    if not exist Dockerfile exit /b 1
                    if not exist tests\\test_api.py exit /b 1
                    if not exist tests\\test_selenium.py exit /b 1

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

        stage('Install Dependencies') {
            steps {
                bat '''
                    @echo off

                    echo Creating Python virtual environment...

                    if not exist ".jenkins-venv\\Scripts\\python.exe" (
                        "%PYTHON_EXE%" -m venv .jenkins-venv
                        if errorlevel 1 exit /b 1
                    )

                    echo Installing testing dependencies...

                    ".jenkins-venv\\Scripts\\python.exe" -m pip install -r requirements-dev.txt
                    if errorlevel 1 exit /b 1

                    echo SUCCESS: Dependencies installed
                '''
            }
        }

        stage('Run Automated Tests') {
            steps {
                script {
                    try {
                        echo 'Checking port 8000 before starting test server...'

                        powershell '''
                            $existing = Get-NetTCPConnection `
                                -LocalPort 8000 `
                                -State Listen `
                                -ErrorAction SilentlyContinue

                            if ($existing) {
                                throw 'Port 8000 is already occupied. Refusing to use an unrelated server.'
                            }

                            if (Test-Path '.jenkins-server.pid') {
                                Remove-Item '.jenkins-server.pid' -Force
                            }
                        '''

                        echo 'Starting temporary Sentinel AI FastAPI server...'

                        powershell '''
                            $python = Join-Path $PWD.Path '.jenkins-venv\\Scripts\\python.exe'

                            $server = Start-Process `
                                -FilePath $python `
                                -ArgumentList @(
                                    '-m',
                                    'uvicorn',
                                    'main:app',
                                    '--host',
                                    '127.0.0.1',
                                    '--port',
                                    '8000'
                                ) `
                                -WorkingDirectory $PWD.Path `
                                -PassThru

                            Set-Content `
                                -Path '.jenkins-server.pid' `
                                -Value $server.Id

                            Write-Host "Started test server PID: $($server.Id)"
                        '''

                        echo 'Waiting for Sentinel AI login page...'

                        powershell '''
                            $ready = $false

                            for ($i = 1; $i -le 30; $i++) {
                                try {
                                    $response = Invoke-WebRequest `
                                        -Uri 'http://127.0.0.1:8000/' `
                                        -UseBasicParsing `
                                        -TimeoutSec 3

                                    if (
                                        $response.StatusCode -eq 200 -and
                                        $response.Content -match 'loginUsername'
                                    ) {
                                        $ready = $true
                                        break
                                    }
                                }
                                catch {
                                    Write-Host "Waiting for server: attempt $i"
                                }

                                Start-Sleep -Seconds 2
                            }

                            if (-not $ready) {
                                throw 'Sentinel AI login page did not become ready.'
                            }

                            Write-Host 'SUCCESS: Sentinel AI login page is ready.'
                        '''

                        echo 'Running automated tests with headless Chrome...'

                        bat '''
                            @echo off

                            if exist test-results.xml del /q test-results.xml

                            ".jenkins-venv\\Scripts\\python.exe" -m pytest -v tests --junitxml=test-results.xml
                            if errorlevel 1 exit /b 1

                            echo SUCCESS: All automated tests passed
                        '''
                    }
                    finally {
                        echo 'Stopping temporary Sentinel AI server...'

                        powershell '''
                            if (Test-Path '.jenkins-server.pid') {
                                $serverPid = Get-Content '.jenkins-server.pid' |
                                    Select-Object -First 1

                                if ($serverPid -match '^\\d+$') {
                                    $serverProcess = Get-CimInstance Win32_Process `
                                        -Filter "ProcessId = $serverPid" `
                                        -ErrorAction SilentlyContinue

                                    if (
                                        $serverProcess -and
                                        $serverProcess.CommandLine -match 'uvicorn'
                                    ) {
                                        Stop-Process `
                                            -Id ([int]$serverPid) `
                                            -Force `
                                            -ErrorAction SilentlyContinue
                                    }
                                }

                                Remove-Item '.jenkins-server.pid' -Force
                            }

                            Write-Host 'Temporary server cleanup completed.'
                        '''
                    }
                }
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
        always {
            echo 'Publishing automated test results...'

            junit allowEmptyResults: true,
                  testResults: 'test-results.xml'

            echo 'Jenkins pipeline execution finished.'
        }

        success {
            echo 'SUCCESS: Sentinel AI CI/CD pipeline completed!'
            echo 'All automated tests passed and Docker image built.'
        }

        failure {
            echo 'FAILED: Check Jenkins Console Output for errors.'
        }
    }
}
