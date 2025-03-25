:: Support installer V1
set venv=%VIRTUAL_ENV%
set venv_path=..\..\venv\Scripts\activate.bat
if "%venv%" == "" (
    if exist "%venv_path%" (
        call "%venv_path%"
    )
)

:: Support installer V2
set environment_path=..\helpers\environment.bat
if exist "%environment_path%" (
    call "%environment_path%"
)

python Updater/updater.py