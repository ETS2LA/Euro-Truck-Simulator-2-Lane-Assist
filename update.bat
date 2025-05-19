set environment_path=..\environment.bat
if exist "%environment_path%" (
    call "%environment_path%"
)

python Updater/updater.py