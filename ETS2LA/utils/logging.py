import logging
from ETS2LA.utils.colors import *
import os

def SetupLogging():
    # Print levels in color
    logging.addLevelName(logging.INFO, f"{DARK_GREEN}[INF]{END}")
    logging.addLevelName(logging.WARNING, f"{DARK_YELLOW}[WRN]{END}")
    logging.addLevelName(logging.ERROR, f"{DARK_RED}[ERR]{END}")
    logging.addLevelName(logging.CRITICAL, f"{RED}[CRT]{END}")

    # Set up logging
    logging.basicConfig(format=
                        f'{DARK_GREY}[%(asctime)s]{END} %(levelname)s {DARK_GREY}%(filename)s{END} \t %(message)s', 
                        level=logging.INFO,
                        datefmt=f'%H:%M:%S'
                        )
    
    # If the log file exists, delete it
    if os.path.exists("ETS2LA.log"):
        os.remove("ETS2LA.log")
    
    # Write the logs to a file
    file_handler = logging.FileHandler("ETS2LA.log")
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
    logging.getLogger().addHandler(file_handler)
    
    logging.info("Logger initialized.")