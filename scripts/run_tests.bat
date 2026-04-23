@echo off
echo Running GW2 Log Score Tests...
echo.

REM Find Python
for /f "delims=" %%i in ('where py') do set PYTHON=%%i
if not defined PYTHON (
    for /f "delims=" %%i in ('where python') do set PYTHON=%%i
)
if not defined PYTHON (
    echo ERROR: Python not found
    exit /b 1
)

echo Using Python: %PYTHON%
echo.

REM Run tests
"%PYTHON%" run_all_tests.py

echo.
echo Test execution completed.
pause
