import logging
from ETS2LA.utils.colors import *

def SetupLogging():
    # Enable color printing on the console
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