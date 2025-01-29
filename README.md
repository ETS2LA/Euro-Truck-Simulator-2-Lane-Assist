This is the rewrite of the entire app backend. There is currently no ETA.

This branch is most likely totally broken, you shouldn't be here unless you're a dev.


### Port usage 
- 37520: Main API
- 37521: Frontend websockets
- 37522: Visualization websockets (position, speed...)
- 3005: Frontend (Can be changed in the settings)
- 60407: Visualization (Godot)

### Installation
If you don't want to use the official installer on the [discord](https://discord.gg/ETS2LA), then you can follow these install steps:
1. Install all requirements, these are `git` and `python 3.11 or 3.12`. Also install `nodejs` if you want to develop the frontend or run it locally.
2. Clone the repository with `git clone https://github.com/ETS2LA/Euro-Truck-Simulator-2-Lane-Assist.git`
3. Run the `update.bat` file to install all dependencies.
 
OR

3. Then install the python dependencies with `pip install -r requirements.txt` in the root folder.
4. Run the app with `python main.py` in the root folder. Use `python main.py --local --dev` to run the frontend in development mode.
