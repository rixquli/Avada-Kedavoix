@echo off
setlocal

cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
	py -3.13 -m venv .venv
	if errorlevel 1 (
		py -3.10 -m venv .venv
		if errorlevel 1 exit /b %errorlevel%
	)
)

".venv\Scripts\python.exe" -m pip install --upgrade pip setuptools wheel
if errorlevel 1 exit /b %errorlevel%

".venv\Scripts\python.exe" -m pip install -r requirements.txt
if errorlevel 1 exit /b %errorlevel%

".venv\Scripts\python.exe" -m PyInstaller --clean --noconfirm AvadaKedavoix.spec
if errorlevel 1 exit /b %errorlevel%
