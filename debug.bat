@echo off

REM Specify the path to the version.txt file
set "version_file=app\version.txt"
REM Specify the path to the log file
set "log_file=app\log.txt"
REM Specify the path to the settings file
set "settings_file=app\profiles\settings.json"
REM Specify the path to the debug.txt file
set "debug_file=debug.txt"

REM Clear the debug.txt file
echo. > "%debug_file%"

REM Check if version.txt exists
if not exist "%version_file%" (
    echo Error: %version_file% not found! >> "%debug_file%"
    echo Error: %version_file% not found!
    exit /b 1
)

REM Display the content of version.txt
set /p version_content=<"%version_file%"
echo Version content: %version_content% >> "%debug_file%"

REM Check if log.txt exists
if not exist "%log_file%" (
    echo Error: %log_file% not found! >> "%debug_file%"
    echo Error: %log_file% not found!
    exit /b 1
)

REM Check if settings.txt exists
if not exist "%settings_file%" (
    echo Error: %settings% not found! >> "%debug_file%"
    echo Error: %settings% not found!
    exit /b 1
)




REM Check if Python is installed
where python > nul 2>&1
if %errorlevel% neq 0 (
    echo Python is not installed! >> "%debug_file%"
    echo Python is not installed!
    exit /b 1
)

REM Get Python version
for /f "tokens=2 delims= " %%v in ('python --version 2^>^&1') do set "python_version=%%v"

REM Display Python version
echo Python version: %python_version%
echo Python version: %python_version% >> "%debug_file%"

REM Display gpus 
echo Gpu: >> "%debug_file%
echo --------------------------- >> "%debug_file%"
wmic path win32_videocontroller get caption >> "%debug_file%"
REM Display the content of log.txt
echo END FILE >> "%debug_file%"
echo Settings file: >> "%debug_file%"
echo --------------------------- >> "%debug_file%"
type "%settings_file%" >> %debug_file%"

REM Display the content of log.txt
echo END FILE >> "%debug_file%"
echo --------------------------- >> "%debug_file%"
echo Log file: >> "%debug_file%"
echo --------------------------- >> "%debug_file%"
type "%log_file%" >> %debug_file%"
echo END FILE >> "%debug_file%"
exit /b 0
