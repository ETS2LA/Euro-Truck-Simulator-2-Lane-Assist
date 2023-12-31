@echo off

REM Quick check
cd %CD%
echo %CD%

REM STEP 1
REM Delete the app folder

if exist %CD%\app (
    rmdir /S /Q %CD%\app
    echo Removed app folder
    pause
) else (
    echo App folder not found
)

REM STEP 2 
REM Delete the start menu entry

set filename=ETS2 Lane Assist.lnk
if exist "C:\Users\%USERNAME%\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\%filename%" (
    del "C:\Users\%USERNAME%\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\%filename%"
    echo Removed start menu entry
    pause
) else (
    echo Start menu entry not found
)

REM STEP 3 
REM TODO: Delete the ViGEmBus driver
REM os.system(f"cd {PATH}")
REM os.system("cd /venv/Lib/site-packages/vgamepad/win/vigem/install/x64")

REM STEP 4
REM Delete the venv folder

if exist %CD%\venv (
    rmdir /S /Q %CD%\venv
    echo Removed venv folder
    pause
) else (
    echo venv folder not found.
)

REM STEP 5
REM Remove everything in the current folder

echo WARNING: This will delete everything in the current folder
paause
rmdir /S /Q %CD%
pause
