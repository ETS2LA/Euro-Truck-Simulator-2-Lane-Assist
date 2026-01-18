dotnet build ETS2LA.sln -c Release --no-incremental
dotnet publish ETS2LA/ETS2LA.csproj --self-contained -r win-x64 -o .\publish