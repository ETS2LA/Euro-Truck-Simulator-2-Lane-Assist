#!/bin/bash

echo "Have you ran '.NET: Build' -> 'All Projects' yet? If you haven't, please do so before running this script."
read -p "Press Enter to continue..."

dotnet publish ETS2LA.UI/ETS2LA.UI.csproj --self-contained -r linux-x64 -o ./publish

read -p "Press Enter to exit..."