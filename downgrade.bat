@echo off
setlocal enabledelayedexpansion

:: Ask the user whether they want to update (checkout rewrite branch and update) or downgrade to a specific commit
echo ============================================
echo Would you like to:
echo 1. Update to the newest version after downgrade
echo 2. Downgrade to a specific commit (no update)
echo ============================================
set /p choice="Choose an option (1-2): "

if "%choice%"=="1" (
    :: Checkout the 'rewrite' branch and run the update process
    echo Checking out the 'rewrite' branch...
    git checkout rewrite
    echo Running the update process...
    goto run_update
)

:: Fetch the latest 5 commits and store them in a temporary file for specific commit downgrade
git log --oneline -5 > commits.txt

:: Initialize counter
set counter=0

:: Read the commits into numbered variables
for /f "tokens=*" %%A in (commits.txt) do (
    set /a counter+=1
    set "commit!counter!=%%A"
)

:: Display the menu for specific commit downgrade options
:menu
cls
echo ============================================
echo   Select a specific commit to downgrade to:
echo ============================================

:: Show the available commits
for /L %%i in (1,1,%counter%) do (
    echo %%i. !commit%%i!
)

echo ============================================
set /p downgrade_choice="Choose a commit to downgrade to (1-%counter%): "

:: Validate the choice
if "%downgrade_choice%"=="" (
    echo Invalid selection.
    pause
    goto menu
)

:: Ensure the choice is a number between 1 and %counter%
for /f "delims=0123456789" %%a in ("%downgrade_choice%") do (
    echo Invalid selection.
    pause
    goto menu
)

if %downgrade_choice% GTR %counter% (
    echo Invalid selection.
    pause
    goto menu
)

if %downgrade_choice% LSS 1 (
    echo Invalid selection.
    pause
    goto menu
)

:: Extract the chosen commit's hash (first 7 characters)
set "commit_line=!commit%downgrade_choice%!"
set "commit_hash=%commit_line:~0,7%"

:: Apply the downgrade by checking out the selected commit
echo Checking out commit %commit_hash%...
git checkout %commit_hash%

echo Downgrade complete.
pause

:: Delete the temporary commits.txt file
del commits.txt

exit

:: Run the update steps after checking out rewrite branch
:run_update
@echo off
git stash
git pull
pip install -r requirements.txt --quiet
echo "Clearing cache, prepare to login again."
RMDIR /S /Q "cache"
echo "Cache cleared"
cd frontend
npm install
cd ..
echo "Update complete"
pause
exit