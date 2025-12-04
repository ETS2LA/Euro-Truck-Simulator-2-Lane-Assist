@echo off
echo "Have you ran `.NET: Build` -> `All Projects` yet? If you haven't, please do so before running this script."
pause
dotnet publish ETS2LA.Backend/ETS2LA.Backend.csproj --self-contained -r win-x64 -o .\publish
pause