@echo off
echo Starting as administrator.
set "params=%*"
cd /d "%~dp0" && ( if exist "%temp%\getadmin.vbs" del "%temp%\getadmin.vbs" ) && fsutil dirty query %systemdrive% 1>nul 2>nul || (  echo Set UAC = CreateObject^("Shell.Application"^) : UAC.ShellExecute "cmd.exe", "/k cd ""%~sdp0"" && ""%~s0"" %params%", "", "runas", 1 >> "%temp%\getadmin.vbs" && "%temp%\getadmin.vbs" && exit /B )
echo Administrator mode enabled.
echo Enabling powershell scripts for this console...
powershell -command "Set-ExecutionPolicy -ExecutionPolicy Unrestricted -Scope Process;echo 'Done, opening script...';.\InstallerSources\installer.ps1"
