#!/bin/bash
# Build the entire project as release (to update plugins)
dotnet build ETS2LA.Linux.slnf -c Release --no-incremental
# Then publish the UI project as a self-contained Linux x64 application
dotnet publish ETS2LA/ETS2LA.csproj --self-contained -r linux-x64 -o ./publish
# Copy the assets folder to the publish dir
cp -r Assets ./publish