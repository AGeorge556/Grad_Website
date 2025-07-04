@echo off
echo ===== Quick Fix for VertexAI Import Error =====
echo.
echo This will fix the "ImportError: cannot import name VertexAI" error
echo.

:: Check if Python is available
where python >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo Python not found in PATH. Please install Python or add it to your PATH.
    pause
    exit /b 1
)

:: Run the quick fix script
echo Running quick fix script...
python quick_fix.py

:: Check if the script ran successfully
if %ERRORLEVEL% neq 0 (
    echo.
    echo Failed to apply quick fix. Please try the full dependency fix:
    echo   - Run fix_dependencies.bat
    pause
    exit /b 1
)

echo.
echo Fix applied successfully!
echo.
echo You can now run your application without the import error.
pause 