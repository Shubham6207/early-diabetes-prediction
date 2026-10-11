@echo off
setlocal
if not exist venv\Scripts\python.exe py -3 -m venv venv
call venv\Scripts\activate.bat
python -m pip install --upgrade pip
pip install -r requirements.txt
if not exist models\diabetes_model.joblib python train_model.py
if errorlevel 1 exit /b 1
python app.py
