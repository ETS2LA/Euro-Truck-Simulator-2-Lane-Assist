import sys
import os

print("""
      __                   ___           _     __ 
     / /  ___ ____  ___   / _ | ___ ___ (_)__ / /_
    / /__/ _ `/ _ \/ -_) / __ |(_-<(_-</ (_-</ __/
   /____/\_,_/_//_/\__/ /_/ |_/___/___/_/___/\__/ 
       _____           _        _ _           
      |_   _|         | |      | | |          
        | |  _ __  ___| |_ __ _| | | ___ _ __ 
        | | | '_ \/ __| __/ _` | | |/ _ \ '__|
       _| |_| | | \__ \ || (_| | | |  __/ |   
      |_____|_| |_|___/\__\__,_|_|_|\___|_|   
                                         
""")

def CreateAnacondaEnvironment():
    # Create a new environment with 
    # pytorch
    # tensorflow
    # and onnx

    # Check that the user has conda
    print("Checking if Anaconda is installed...")
    import subprocess
    try:
        subprocess.check_call(["conda.bat", "--version"])
        print("> Conda is installed!\n")
    except Exception as ex:
        print(ex)
        print("> Not installed, install it here https://www.anaconda.com/...")
        print("> If you have installed it, make sure it is added to PATH...")
        print("> And then run this script again...")
        
        sys.exit(0)

    input("""
The script will now create and configure a new anaconda environment named LaneAssist.
This will take a while, so please be patient.
> Press Enter to continue...""")

    # Run the following command in command prompt
    print("\nCreating Anaconda Environment...")
    try:
        os.system("conda create -n LaneAssist python=3.9 --yes")
        os.system("conda activate LaneAssist")
        #os.system("conda install pytorch torchvision torchaudio pytorch-cuda=11.7 -c pytorch -c nvidia --yes")
        #os.system("conda install tensorflow-gpu --yes")
        #os.system("conda install -c conda-forge onnx --yes")
        #os.system("conda install -c conda-forge onnxruntime-gpu --yes")
        #os.system("conda install -c conda-forge cudnn --yes")
    except Exception as ex:
        print("Error while creating Anaconda Environment...")
        print(ex)
        sys.exit(0)

CreateAnacondaEnvironment()