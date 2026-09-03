$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

$projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $projectRoot

Write-Host "==================================================" -ForegroundColor Cyan
Write-Host " Corporate Knowledge Assistant - setup" -ForegroundColor Cyan
Write-Host "==================================================" -ForegroundColor Cyan

function Ensure-Command {
    param(
        [string]$Name,
        [string]$InstallHint
    )

    $command = Get-Command $Name -ErrorAction SilentlyContinue
    if (-not $command) {
        Write-Host "Command '$Name' not found. $InstallHint" -ForegroundColor Red
        throw "Missing required command: $Name"
    }
}

# Check Python 3.11+
$pythonCommand = $null
if (Get-Command py -ErrorAction SilentlyContinue) {
    $pythonVersionCheck = & py -3 -c "import sys; print(sys.version_info[:2])" 2>$null
    if ($LASTEXITCODE -eq 0 -and $pythonVersionCheck) {
        $pythonCommand = "py -3"
    }
}
if (-not $pythonCommand -and (Get-Command python -ErrorAction SilentlyContinue)) {
    $pythonVersionCheck = & python -c "import sys; print(sys.version_info[:2])" 2>$null
    if ($LASTEXITCODE -eq 0 -and $pythonVersionCheck) {
        $pythonCommand = "python"
    }
}
if (-not $pythonCommand) {
    Write-Host "Python 3.11+ is required. Install Python and reopen this script." -ForegroundColor Red
    throw "Python 3.11+ not found"
}

$pythonVersionString = & py -3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')" 2>$null
if ($LASTEXITCODE -ne 0) {
    $pythonVersionString = & python -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')" 2>$null
}
if ($pythonVersionString) {
    $versionMajorMinor = [version]$pythonVersionString
    if ($versionMajorMinor -lt [version]"3.11") {
        Write-Host "Python version is $pythonVersionString, but 3.11+ is required." -ForegroundColor Red
        throw "Unsupported Python version"
    }
}

# Ensure uv
if (-not (Get-Command uv -ErrorAction SilentlyContinue)) {
    Write-Host "Installing uv..." -ForegroundColor Yellow
    if (Get-Command winget -ErrorAction SilentlyContinue) {
        winget install --id=astral-sh.uv -e
    }
    elseif (Get-Command choco -ErrorAction SilentlyContinue) {
        choco install uv -y
    }
    else {
        Write-Host "Please install uv manually: https://docs.astral.sh/uv/getting-started/installation/" -ForegroundColor Red
        throw "uv is not installed"
    }

    if (-not (Get-Command uv -ErrorAction SilentlyContinue)) {
        throw "uv was not installed successfully"
    }
}

Write-Host "Creating virtual environment..." -ForegroundColor Yellow
if (Test-Path ".venv") {
    Write-Host "Existing virtual environment found. Recreating it in non-interactive mode..." -ForegroundColor Yellow
    uv venv --python 3.11 --clear .venv
}
else {
    uv venv --python 3.11 .venv
}

Write-Host "Installing project dependencies..." -ForegroundColor Yellow
uv sync

if (-not (Test-Path .env)) {
    @'
POSTGRES_HOST=localhost
POSTGRES_PORT=5433
POSTGRES_DB=rag_db
POSTGRES_USER=rag_user
POSTGRES_PASSWORD=rag_password
HF_HUB_DISABLE_TELEMETRY=1
'@ | Set-Content -Path .env
    Write-Host "Created .env with default settings." -ForegroundColor Green
}
else {
    Write-Host ".env already exists; leaving it unchanged." -ForegroundColor Green
}

$dockerExists = Get-Command docker -ErrorAction SilentlyContinue
if ($dockerExists) {
    $dockerComposeVersion = & docker compose version 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "Starting PostgreSQL with Docker Compose..." -ForegroundColor Yellow
        docker compose up -d --wait
    }
    else {
        Write-Host "Docker is installed, but docker compose is unavailable. Skipping database startup." -ForegroundColor Yellow
    }
}
else {
    Write-Host "Docker was not found. Skipping database startup. Install Docker Desktop to run PostgreSQL automatically." -ForegroundColor Yellow
}

Write-Host "Applying database migrations..." -ForegroundColor Yellow
uv run alembic upgrade head

Write-Host "Checking database connection..." -ForegroundColor Yellow
$connectionCheck = uv run python -c "from app.database import get_connection; conn = get_connection(); print('OK'); conn.close()" 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "Database is not yet ready or Docker is not running. Check .env and PostgreSQL settings." -ForegroundColor Yellow
}
else {
    Write-Host $connectionCheck -ForegroundColor Green
}

Write-Host "" 
Write-Host "Setup finished successfully." -ForegroundColor Green
Write-Host "Next step: run the app with the command below." -ForegroundColor Green
Write-Host "" 
Write-Host "uv run uvicorn app.main:app --reload" -ForegroundColor Cyan
Write-Host "Then open: http://localhost:8000" -ForegroundColor Cyan
Write-Host "" 
Write-Host "If you want to start it immediately, run start.bat" -ForegroundColor Cyan

$startNow = Read-Host "Start the app now? (Y/N)"
if ($startNow -match '^(Y|y|YES|yes)$') {
    Write-Host "Launching the application..." -ForegroundColor Yellow
    Start-Process "cmd.exe" -ArgumentList "/k", "uv run uvicorn app.main:app --reload"
}
