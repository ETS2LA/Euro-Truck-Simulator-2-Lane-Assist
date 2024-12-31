set venv=%VIRTUAL_ENV%
set venv_path=..\..\venv\Scripts\activate.bat
if "%venv%" == "" (
    if exist "%venv_path%" (
        call "%venv_path%"
    )
)
python Updater/updater.py