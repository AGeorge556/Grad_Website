@echo off
echo ===== Dependency Conflict Fix Script =====
echo.

:: Check if Python is available
where python >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo Python not found in PATH. Please install Python or add it to your PATH.
    pause
    exit /b 1
)

echo Choose a fix method:
echo 1. Standard fix (tries to maintain version ranges)
echo 2. Alternative fix (uses specific older versions)
echo.

set /p choice="Enter your choice (1 or 2): "

if "%choice%"=="1" (
    echo.
    echo Running standard dependency fix script...
    python fix_dependencies.py
) else if "%choice%"=="2" (
    echo.
    echo Running alternative dependency fix script...
    python fix_dependencies_alt.py
) else (
    echo.
    echo Invalid choice. Please run the script again and enter 1 or 2.
    pause
    exit /b 1
)

:: Check if the script ran successfully
if %ERRORLEVEL% neq 0 (
    echo.
    echo Failed to fix dependencies. Please check the error messages above.
    echo Try the other fix method or contact support.
    pause
    exit /b 1
)

echo.
echo Dependencies fixed successfully!
echo.
echo You can now run your application without conflicts.
pause 