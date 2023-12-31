winget --version >nul 2>&1 || (
    color 4 & echo WARNING, You do not have winget avialble on your system, This is most lickly because your on a windows version older then 2004. Please update your windows install and try again.
    pause
    exit 0
)

git --version >nul 2>&1 || (
    color 6 & echo Installing git, Please read and accept the windows smart screen prompt
    winget install Git.Git
    echo git is now installed
)

python --version >nul 2>&1 || (
    color 6 & echo Installing python, Please read and accept the windows smart screen prompt
    winget install -e --id Python.Python.3.11
    echo Python is now installed
)
:start

if exist installer.py (
    python --version >nul 2>&1 || (
        color 2 & echo Successfully install all requirements please re run installer.bat
        pause
        exit 0
    )
    python installer.py
    
) else (
    git --version >nul 2>&1 || (
        color 2 & echo Successfully install all requirements please re run installer.bat
        pause
        exit 0
    )
    git clone -b installer https://github.com/Tumppi066/Euro-Truck-Simulator-2-Lane-Assist.git
    xcopy Euro-Truck-Simulator-2-Lane-Assist\* . /E /H /C /Y
    rmdir /S /Q Euro-Truck-Simulator-2-Lane-Assist
    color 2 & echo Successfully installed installer
    color 7
    python installer.py
    pause
    
)

pause
