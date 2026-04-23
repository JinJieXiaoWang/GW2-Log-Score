$projectDir = "D:\Code\GW2-Log-Score"
$testScript = "run_all_tests.py"
$pythonExe = "C:\Users\Administrator\AppData\Local\Programs\Python\Python312\python.exe"

$scriptPath = Join-Path $projectDir $testScript

Write-Host "Starting Python process..." -ForegroundColor Cyan
Write-Host "Python: $pythonExe"
Write-Host "Script: $scriptPath"

$process = Start-Process -FilePath $pythonExe -ArgumentList $scriptPath -WorkingDirectory $projectDir -PassThru -NoNewWindow

$process.WaitForExit()

Write-Host ""
Write-Host "Exit Code: $($process.ExitCode)"
