dotnet build ETS2LA.sln -c Release --no-incremental
dotnet publish ETS2LA/ETS2LA.csproj --self-contained -o .\publish
xcopy /E /I /Y .\Assets .\publish\Assets