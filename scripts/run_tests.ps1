Write-Host "GW2 Log Score - Running Tests" -ForegroundColor Cyan
Write-Host "=" * 60

$pythonCmd = $null
try {
    $pythonCmd = Get-Command py -ErrorAction SilentlyContinue
    if (-not $pythonCmd) {
        $pythonCmd = Get-Command python -ErrorAction SilentlyContinue
    }
} catch {}

if (-not $pythonCmd) {
    Write-Host "ERROR: Python not found" -ForegroundColor Red
    exit 1
}

Write-Host "Using Python: $($pythonCmd.Source)" -ForegroundColor Green
Write-Host ""

# Run tests
& $pythonCmd.Source "run_all_tests.py"

Write-Host ""
Write-Host "Test execution completed." -ForegroundColor Cyan
