@echo off
echo ========================================
echo WhatsApp Bulk Sender - Installation
echo ========================================

echo Creating virtual environment...
python -m venv venv

echo Activating virtual environment...
call venv\Scripts\activate

echo Upgrading pip...
python -m pip install --upgrade pip

echo Installing requirements...
pip install -r requirements.txt

echo Creating .env file...
if not exist .env (
    echo GROQ_API_KEY=your_groq_api_key_here > .env
    echo DEBUG=True >> .env
    echo SECRET_KEY=your-secret-key-here >> .env
)

echo Creating directories...
mkdir whatsapp_profile 2>nul
mkdir static 2>nul
mkdir media 2>nul
mkdir logs 2>nul

echo.
echo ========================================
echo Installation Complete!
echo ========================================
echo.
echo Next steps:
echo 1. Add your Groq API key to .env file
echo 2. Run: python manage.py runserver
echo 3. Open http://localhost:8000
echo.
pause