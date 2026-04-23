$pythonExe = "C:\Users\Administrator\AppData\Local\Programs\Python\Python313\python.exe"
$projectDir = "D:\Code\GW2-Log-Score"
$testScript = "run_all_tests.py"

Write-Host "=== GW2日志评分系统 - 沙盒环境测试 ===" -ForegroundColor Cyan
Write-Host "Python路径: $pythonExe" -ForegroundColor Green
Write-Host "项目目录: $projectDir" -ForegroundColor Green
Write-Host "测试脚本: $testScript" -ForegroundColor Green
Write-Host ""

if (-not (Test-Path $pythonExe)) {
    Write-Host "[ERROR] Python未找到: $pythonExe" -ForegroundColor Red
    exit 1
}

if (-not (Test-Path (Join-Path $projectDir $testScript))) {
    Write-Host "[ERROR] 测试脚本未找到: $testScript" -ForegroundColor Red
    exit 1
}

Write-Host "[1/4] 验证Python版本..." -ForegroundColor Yellow
& $pythonExe --version
Write-Host ""

Write-Host "[2/4] 验证项目依赖..." -ForegroundColor Yellow
& $pythonExe -m pip list 2>&1 | Select-String "fastapi|uvicorn|pandas|openpyxl"
Write-Host ""

Write-Host "[3/4] 启动测试套件..." -ForegroundColor Yellow
Write-Host "----------------------------------------" -ForegroundColor Gray

$startTime = Get-Date

$process = Start-Process -FilePath $pythonExe -ArgumentList $testScript -WorkingDirectory $projectDir -NoNewWindow -Wait -PassThru

$endTime = Get-Date
$duration = ($endTime - $startTime).TotalSeconds

Write-Host "----------------------------------------" -ForegroundColor Gray
Write-Host ""
Write-Host "[4/4] 测试完成！" -ForegroundColor Yellow
Write-Host "执行耗时: $([math]::Round($duration, 2)) 秒" -ForegroundColor Cyan
Write-Host "退出码: $($process.ExitCode)" -ForegroundColor $(if ($process.ExitCode -eq 0) { "Green" } else { "Red" })

if ($process.ExitCode -eq 0) {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "        所有测试通过！" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
    exit 0
} else {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Red
    Write-Host "        部分测试失败，请检查" -ForegroundColor Red
    Write-Host "========================================" -ForegroundColor Red
    exit $process.ExitCode
}
