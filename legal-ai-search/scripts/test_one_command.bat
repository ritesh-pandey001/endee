@echo off
REM One-Command Test for Recruiters
REM This tests if the server is running and validates core functionality

echo ================================================
echo   AI Legal Assistant - One-Command Test
echo ================================================
echo.

echo Checking if server is running...
curl -s http://localhost:8000/health >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Server is not running!
    echo.
    echo Please start the server first:
    echo   python -m app.main
    echo.
    echo Then run this test again.
    pause
    exit /b 1
)

echo [OK] Server is running
echo.
echo Running comprehensive validation tests...
echo.

powershell -ExecutionPolicy Bypass -File "%~dp0test_quick.ps1"

echo.
echo ================================================
echo   Test Complete
echo ================================================
echo.
pause
