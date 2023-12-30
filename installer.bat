@echo off
git --version >nul 2>&1 || (
    echo Installing git, Please read and accept the windows smart screen prompt
    msg * "Installing git, Please read and accept the windows smart screen prompt"
    powershell -Command "(New-Object Net.WebClient).DownloadFile('https://github.com/git-for-windows/git/releases/download/v2.43.0.windows.1/Git-2.43.0-64-bit.exe', 'git_installer.exe')"
    git_installer.exe /VERYSILENT /NORESTART /NOCANCEL /SP-
    del git_installer.exe
    echo git is now installed
    msg * "git is now installed"
)

python --version >nul 2>&1 || (
    echo Installing python, Please read and accept the windows smart screen prompt
    msg * "Installing python, Please read and accept the windows smart screen prompt"
    powershell -Command "(New-Object Net.WebClient).DownloadFile('https://www.python.org/ftp/python/3.11.6/python-3.11.6-amd64.exe', 'python_installer.exe')"
    python_installer.exe /quiet InstallAllUsers=1 PrependPath=1 Include_test=0
    del python_installer.exe
    msg * "Python is now installed rerun installer.bat"
    echo Python is now installed rerun installer.bat
    exit 0
)

python installer.py
pause
