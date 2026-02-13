@echo off
echo ========================================
echo 2moreFitness Gym Management System
echo Installation Script for Windows
echo ========================================
echo.

echo [1/6] Creating virtual environment...
python -m venv venv
if errorlevel 1 (
    echo ERROR: Failed to create virtual environment
    pause
    exit /b 1
)

echo [2/6] Activating virtual environment...
call venv\Scripts\activate.bat

echo [3/6] Installing dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)

echo [4/6] Running database migrations...
python manage.py makemigrations
python manage.py migrate
if errorlevel 1 (
    echo ERROR: Database migration failed
    pause
    exit /b 1
)

echo [5/6] Creating superuser...
echo.
echo Please create an admin account:
python manage.py createsuperuser

echo [6/6] Loading sample data...
python manage.py shell < setup_sample_data.py

echo.
echo ========================================
echo Installation Complete!
echo ========================================
echo.
echo To start the server, run:
echo   venv\Scripts\activate
echo   python manage.py runserver
echo.
echo Then visit: http://127.0.0.1:8000/
echo.
pause
