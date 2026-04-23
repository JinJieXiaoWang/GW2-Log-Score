$projectDir = "D:\Code\GW2-Log-Score"
$testScript = "run_all_tests.py"

Write-Host "Searching for Python installation..." -ForegroundColor Cyan

# Try to find Python
$pythonCmd = $null

# Method 1: Check common locations
$possiblePaths = @(
    "C:\Python312\python.exe",
    "C:\Python311\python.exe",
    "C:\Python310\python.exe",
    "C:\Program Files\Python312\python.exe",
    "C:\Program Files (x86)\Python312\python.exe"
)

foreach ($path in $possiblePaths) {
    if (Test-Path $path) {
        $pythonCmd = $path
        Write-Host "Found Python at: $pythonCmd" -ForegroundColor Green
        break
    }
}

# Method 2: Try py launcher
if (-not $pythonCmd) {
    try {
        $pyOutput = & py -c "import sys; print(sys.executable)" 2>$null
        if ($pyOutput -and (Test-Path $pyOutput)) {
            $pythonCmd = $pyOutput
            Write-Host "Found Python via py launcher: $pythonCmd" -ForegroundColor Green
        }
    } catch {}
}

# Method 3: Try python command
if (-not $pythonCmd) {
    try {
        $pyOutput = & python -c "import sys; print(sys.executable)" 2>$null
        if ($pyOutput -and (Test-Path $pyOutput)) {
            $pythonCmd = $pyOutput
            Write-Host "Found Python via python command: $pythonCmd" -ForegroundColor Green
        }
    } catch {}
}

# Method 4: Check WindowsApps python
if (-not $pythonCmd) {
    $windowsAppsPython = "C:\Users\Administrator\AppData\Local\Microsoft\WindowsApps\python.exe"
    if ((Test-Path $windowsAppsPython) -and ((Get-Item $windowsAppsPython).Length -gt 1KB)) {
        $pythonCmd = $windowsAppsPython
        Write-Host "Using WindowsApps Python: $pythonCmd" -ForegroundColor Green
    }
}

if (-not $pythonCmd) {
    Write-Host "ERROR: Could not find a working Python installation" -ForegroundColor Red
    Write-Host "Please install Python 3.9 or higher" -ForegroundColor Red
    exit 1
}

# Check test script
$scriptPath = Join-Path $projectDir $testScript
if (-not (Test-Path $scriptPath)) {
    Write-Host "ERROR: Test script not found at: $scriptPath" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "Running tests..." -ForegroundColor Cyan
Write-Host "=" * 60

# Try to run using Start-Process
try {
    $pinfo = New-Object System.Diagnostics.ProcessStartInfo
    $pinfo.FileName = $pythonCmd
    $pinfo.Arguments = $scriptPath
    $pinfo.WorkingDirectory = $projectDir
    $pinfo.RedirectStandardOutput = $true
    $pinfo.RedirectStandardError = $true
    $pinfo.UseShellExecute = $false
    $pinfo.CreateNoWindow = $true

    $p = New-Object System.Diagnostics.Process
    $p.StartInfo = $pinfo
    $p.Start() | Out-Null

    $stdout = $p.StandardOutput.ReadToEnd()
    $stderr = $p.StandardError.ReadToEnd()
    $p.WaitForExit()

    Write-Host $stdout
    if ($stderr) {
        Write-Host "STDERR: $stderr" -ForegroundColor Red
    }

    $exitCode = $p.ExitCode
} catch {
    Write-Host "Error running Python: $_" -ForegroundColor Red
    $exitCode = 1
}

Write-Host ""
Write-Host "=" * 60
if ($exitCode -eq 0) {
    Write-Host "ALL TESTS PASSED!" -ForegroundColor Green
} else {
    Write-Host "Tests completed. Exit code: $exitCode" -ForegroundColor Yellow
}

exit $exitCode
