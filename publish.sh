#!/bin/bash
dotnet tool restore

dotnet build ETS2LA.Linux.slnf -c Release --no-incremental
dotnet publish ETS2LA/ETS2LA.csproj --self-contained -r linux-x64 -o ./publish

# Copy the assets folder to the publish dir
cp -r Assets ./publish
cp -r ETS2LA.UI/wwwroot ./publish