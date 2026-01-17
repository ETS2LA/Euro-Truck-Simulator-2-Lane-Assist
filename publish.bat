dotnet build ETS2LA.sln -c Release --no-incremental
dotnet publish ETS2LA.UI/ETS2LA.UI.csproj --self-contained -r win-x64 -o .\publish