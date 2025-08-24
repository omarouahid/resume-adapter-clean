@echo off
echo 🚀 Resume to LaTeX Generator
echo ==============================

:: Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://python.org
    pause
    exit /b 1
)

:: Check if app.py exists
if not exist "app.py" (
    echo ❌ app.py not found. Please run this from the project directory.
    pause
    exit /b 1
)

echo 📦 Checking dependencies...
python test_setup.py
if errorlevel 1 (
    echo.
    echo ❌ Setup test failed. Please install dependencies:
    echo    pip install -r requirements.txt
    pause
    exit /b 1
)

echo.
echo 🌐 Starting Streamlit application...
echo 📝 The app will open in your browser
echo 🔑 Remember to add your OpenRouter API key in the sidebar
echo.
echo ⏹️  Press Ctrl+C to stop the application
echo ==============================

python -m streamlit run app.py --server.headless false --server.port 8501

pause


