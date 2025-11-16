@echo off
REM The London Lark - Event Scraper Quick Start (Windows)
REM ======================================================

echo.
echo ============================================================
echo   🕊️  THE LONDON LARK - Event Scraper
echo   Quick Start for Windows
echo ============================================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed or not in PATH!
    echo    Please install Python from: https://www.python.org/downloads/windows/
    echo.
    pause
    exit /b 1
)

echo Python found:
python --version
echo.

REM Check if dependencies are installed
python -c "import requests; import bs4" >nul 2>&1
if errorlevel 1 (
    echo Installing dependencies...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo ❌ Failed to install dependencies!
        echo    Try running: pip install requests beautifulsoup4 lxml
        pause
        exit /b 1
    )
    echo ✅ Dependencies installed!
    echo.
)

REM Run the scraper
echo Starting scraper...
echo.

python local_scraper.py --days 7

echo.
echo Done! Check scraped_events.json for results.
echo.
pause
