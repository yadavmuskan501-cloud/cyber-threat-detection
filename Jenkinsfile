
pipeline {
    agent any

    environment {
        DOCKER_BIN = 'C:\\Users\\cpulk\\AppData\\Local\\Programs\\DockerDesktop\\resources\\bin'
        PYTHON_EXE = 'C:\\Users\\cpulk\\AppData\\Local\\Python\\pythoncore-3.12-64\\python.exe'
        HEADLESS = '1'
        SENTINEL_ENV = 'test'
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

                    def configCreated = false

                    try {

                        echo 'Checking test environment...'

                        powershell '''
                            $ErrorActionPreference = 'Stop'

                            if (Test-Path '.env.test') {
                                throw 'Existing .env.test found. Remove it securely before continuing.'
                            }

                            if (Test-Path 'test-results.xml') {
                                Remove-Item 'test-results.xml' -Force
                            }

                            $existing = Get-NetTCPConnection `
                                -LocalPort 8000 `
                                -State Listen `
                                -ErrorAction SilentlyContinue

                            if ($existing) {
                                throw 'Port 8000 is already occupied.'
                            }

                            if (Test-Path '.jenkins-server.pid') {
                                Remove-Item '.jenkins-server.pid' -Force
                            }
                        '''

                        echo 'Configuring MongoDB testing credentials...'

                        withCredentials([
                            file(
                                credentialsId: 'sentinel_mongodb_test',
                                variable: 'MONGO_CONFIG'
                            )
                        ]) {

                            configCreated = true

                            powershell '''
                                $ErrorActionPreference = 'Stop'

                                Copy-Item `
                                    -LiteralPath $env:MONGO_CONFIG `
                                    -Destination '.env.test'

                                Write-Host 'SUCCESS: Test configuration installed.'
                            '''

                            echo 'Validating MongoDB test configuration...'

                            bat '''
                                @echo off

                                ".jenkins-venv\\Scripts\\python.exe" -c "from dotenv import dotenv_values; c=dotenv_values('.env.test'); assert all(c.get(k) for k in ['MONGODB_USERNAME','MONGODB_PASSWORD','MONGODB_HOST','MONGODB_DB_NAME']), 'Missing MongoDB configuration'; assert c['MONGODB_DB_NAME']=='sentinelai_test', 'Unsafe database name'; assert c['MONGODB_USERNAME']=='sentinelai_test_user', 'Unsafe database user'; print('SUCCESS: Test database configuration validated')"

                                if errorlevel 1 exit /b 1
                            '''

                            echo 'Checking MongoDB connectivity...'

                            bat '''
                                @echo off

                                ".jenkins-venv\\Scripts\\python.exe" -c "from database import client; client.admin.command('ping'); print('SUCCESS: MongoDB connection verified')"

                                if errorlevel 1 exit /b 1
                            '''

                            echo 'Starting temporary Sentinel AI FastAPI server...'

                            powershell '''
                                $ErrorActionPreference = 'Stop'

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
                                    -RedirectStandardOutput '.jenkins-server-out.log' `
                                    -RedirectStandardError '.jenkins-server-error.log' `
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

                                    $serverPid = Get-Content '.jenkins-server.pid' |
                                        Select-Object -First 1

                                    $process = Get-Process `
                                        -Id ([int]$serverPid) `
                                        -ErrorAction SilentlyContinue

                                    if (-not $process) {
                                        Write-Host 'ERROR: FastAPI server exited.'
                                        break
                                    }

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
                                    throw 'Sentinel AI login page did not become ready. Inspect the server error log privately.'
                                }

                                Write-Host 'SUCCESS: Sentinel AI login page is ready.'
                            '''

                            echo 'Preparing Selenium test account...'

                            powershell '''
                                $baseUrl = 'http://127.0.0.1:8000'

                                $credentials = @{
                                    username = 'analyst2'
                                    email    = 'analyst2@example.com'
                                    password = 'ExamplePass123!'
                                }

                                $registrationBody = $credentials |
                                    ConvertTo-Json

                                $loginBody = @{
                                    username = $credentials.username
                                    password = $credentials.password
                                } | ConvertTo-Json

                                try {
                                    $null = Invoke-RestMethod `
                                        -Uri "$baseUrl/api/auth/register" `
                                        -Method POST `
                                        -ContentType 'application/json' `
                                        -Body $registrationBody `
                                        -ErrorAction Stop

                                    Write-Host 'Selenium test account registered.'
                                }
                                catch {
                                    Write-Host 'Registration unsuccessful; checking existing account.'
                                }

                                try {
                                    $login = Invoke-RestMethod `
                                        -Uri "$baseUrl/api/auth/login" `
                                        -Method POST `
                                        -ContentType 'application/json' `
                                        -Body $loginBody `
                                        -ErrorAction Stop

                                    if ($login.status -ne 'Authenticated') {
                                        throw 'Unexpected authentication response.'
                                    }

                                    Write-Host 'SUCCESS: Selenium test account authenticated.'
                                }
                                catch {
                                    throw 'Selenium test account setup failed.'
                                }
                            '''

                            echo 'Running automated tests with headless Chrome...'

                            catchError(
                                buildResult: 'FAILURE',
                                stageResult: 'FAILURE'
                            ) {
                                bat '''
                                    @echo off

                                    ".jenkins-venv\\Scripts\\python.exe" -m pytest -v tests --junitxml=test-results.xml

                                    if errorlevel 1 exit /b 1

                                    echo SUCCESS: All automated tests passed
                                '''
                            }
                        }
                    }

                    finally {

                        echo 'Stopping temporary Sentinel AI server...'

                        try {
                            powershell '''
                                $ErrorActionPreference = 'Stop'

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
                                                -ErrorAction Stop
                                        }
                                    }

                                    Remove-Item '.jenkins-server.pid' -Force
                                }

                                Write-Host 'Temporary server cleanup completed.'
                            '''
                        }

                        finally {
                            if (configCreated) {

                                echo 'Removing temporary MongoDB configuration...'

                                powershell '''
                                    $ErrorActionPreference = 'Stop'

                                    if (Test-Path '.env.test') {
                                        Remove-Item '.env.test' -Force
                                    }

                                    Write-Host 'SUCCESS: Temporary configuration removed.'
                                '''
                            }
                        }
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

                    if exist .env.test exit /b 1
                    if exist .env exit /b 1

                    if exist .jenkins-server-out.log del /q .jenkins-server-out.log
                    if exist .jenkins-server-error.log del /q .jenkins-server-error.log

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
