@echo off
SET FLASK_APP=app.py
SET FLASK_ENV=production

:: Ativa o ambiente virtual venv
CALL C:\Users\Biina\Desktop\doce-controle\venv\Scripts\activate.bat

:: Inicia o servidor com Waitress
python -m waitress --host=0.0.0.0 --port=8080 app:app

pause
