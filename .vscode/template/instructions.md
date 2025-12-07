## Installation
Navigate to this folder in your terminal. Then write the following:
```bash
dotnet new --install .
```
Now if you run:
```bash
dotnet new list
```
You should see `ets2la-plugin` in the list of installed templates. You should now refresh your VS Code window to make the template available.

## Usage
Press F1 in VS Code and type `> .NET: New Project...`, then select `ETS2LA Plugin` from the list of templates. 
> When prompted to select a folder **select the /Plugins folder** in the root directory!

After you've created your project it's recommended to change the .csproj filename to match your plugin name. After you've done this you'll have to edit the main `ETS2LA.sln` solution file to change the reference to your new .csproj filename.