# GW2 Log Score - Virtual Environment Setup Script
# This script creates a dedicated virtual environment for this project

param(
    [switch]$Recreate  # Use -Recreate to delete existing venv and create fresh
)

$ErrorActionPreference = "Stop"
$ProjectRoot = Split-Path -Parent $PSScriptRoot
$VenvPath = Join-Path $ProjectRoot "venv"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "GW2 Log Score - Virtual Environment Setup" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if venv exists
if (Test-Path $VenvPath) {
    if ($Recreate) {
        Write-Host "[INFO] Removing existing virtual environment..." -ForegroundColor Yellow
        Remove-Item -Recurse -Force $VenvPath
    } else {
        Write-Host "[INFO] Virtual environment already exists at: $VenvPath" -ForegroundColor Green
        Write-Host "[INFO] To recreate, run: .\setup_venv.ps1 -Recreate" -ForegroundColor Gray
        Write-Host ""
        Write-Host "To activate the virtual environment, run:" -ForegroundColor Cyan
        Write-Host "    .\venv\Scripts\Activate.ps1" -ForegroundColor Yellow
        return
    }
}

# Create virtual environment
Write-Host "[1/3] Creating virtual environment..." -ForegroundColor Cyan
python -m venv $VenvPath

if (-not (Test-Path $VenvPath)) {
    Write-Host "[ERROR] Failed to create virtual environment" -ForegroundColor Red
    exit 1
}

Write-Host "[OK] Virtual environment created at: $VenvPath" -ForegroundColor Green

# Activate virtual environment
$VenvPython = Join-Path $VenvPath "Scripts" | Join-Path -ChildPath "python.exe"
$VenvPip = Join-Path $VenvPath "Scripts" | Join-Path -ChildPath "pip.exe"

Write-Host ""
Write-Host "[2/3] Upgrading pip..." -ForegroundColor Cyan
& $VenvPython -m pip install --upgrade pip --quiet

Write-Host ""
Write-Host "[3/3] Installing dependencies..." -ForegroundColor Cyan

# Define dependencies
$Dependencies = @(
    "fastapi",
    "uvicorn",
    "python-multipart",
    "pandas",
    "openpyxl"
)

$FailedPackages = @()

foreach ($Package in $Dependencies) {
    Write-Host "    Installing $Package..." -NoNewline
    try {
        & $VenvPip install $Package --quiet 2>$null
        Write-Host " [OK]" -ForegroundColor Green
    } catch {
        Write-Host " [FAILED]" -ForegroundColor Red
        $FailedPackages += $Package
    }
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan

if ($FailedPackages.Count -eq 0) {
    Write-Host "[SUCCESS] All dependencies installed successfully!" -ForegroundColor Green
} else {
    Write-Host "[WARNING] Some packages failed to install: $($FailedPackages -join ', ')" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Setup Complete!" -ForegroundColor Green
Write-Host ""
Write-Host "To activate the virtual environment, run:" -ForegroundColor Cyan
Write-Host "    .\venv\Scripts\Activate.ps1" -ForegroundColor Yellow
Write-Host ""
Write-Host "To start the server, run:" -ForegroundColor Cyan
Write-Host "    .\venv\Scripts\python.exe start.py --serve" -ForegroundColor Yellow
Write-Host ""
Write-Host "To deactivate the virtual environment, run:" -ForegroundColor Cyan
Write-Host "    deactivate" -ForegroundColor Yellow
Write-Host ""
