@echo off
SETLOCAL EnableDelayedExpansion

REM Save current directory
SET start_dir=%CD%

echo Starting update process...

REM Stash and pull changes
git stash || (
    echo Failed to save current repository state
    goto :error
)

git pull || (
    echo Failed to pull updates from repository
    goto :error
)

REM Update Python dependencies
pip install -r requirements.txt || (
    echo Failed to update python dependencies
    goto :error
)

echo Clearing cache, prepare to login again after update...
RMDIR /S /Q "cache" 2>nul
echo Cache cleared

REM Frontend updates
cd frontend || (
    echo Could not access frontend directory
    goto :error
)

call npm i || (
    echo NPM install failed
    cd %start_dir%
    goto :error
)

call npm run build || (
    echo Build failed
    cd %start_dir%
    goto :error
)

cd %start_dir%
echo Update completed successfully
exit /b 0

:error
echo Update failed
exit /b 1