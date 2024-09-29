@echo off
setlocal enabledelayedexpansion

:: Fetch the latest 5 commits and store them in a temporary file
git log --oneline -5 > commits.txt

:: Initialize counter
set counter=0

:: Read the commits into numbered variables
for /f "tokens=*" %%A in (commits.txt) do (
    set /a counter+=1
    set "commit!counter!=%%A"
)

:: Display the menu
:menu
cls
echo ============================================
echo   Select a recent update to apply:
echo ============================================

:: Show the available commits
for /L %%i in (1,1,%counter%) do (
    echo %%i. !commit%%i!
)

echo ============================================
set /p choice=Choose an option (1-%counter%): 

:: Validate the choice
if "%choice%"=="" (
    echo Invalid selection.
    pause
    goto menu
)

:: Ensure the choice is a number between 1 and %counter%
for /f "delims=0123456789" %%a in ("%choice%") do (
    echo Invalid selection.
    pause
    goto menu
)

if %choice% GTR %counter% (
    echo Invalid selection.
    pause
    goto menu
)

if %choice% LSS 1 (
    echo Invalid selection.
    pause
    goto menu
)

:: Extract the chosen commit's hash (first 7 characters)
set "commit_line=!commit%choice%!"
set "commit_hash=%commit_line:~0,7%"

:: Apply the selected update (checkout the commit)
echo Checking out commit %commit_hash%...
git checkout %commit_hash%

:: Run the update steps
:run_update
git stash
git pull
pip install -r requirements.txt --quiet
echo Clearing cache, prepare to login again.
RMDIR /S /Q cache
echo Cache cleared
cd frontend
npm install
cd ..

:: Delete the temporary commits.txt file
del commits.txt

echo Update complete
pause
exit