"""
This file handles both the main logger as well as the
plugin specific logger.

Plugins by default only log warning and up to the console,
but all logs are writte to /logs
"""
from rich.highlighter import NullHighlighter, Highlighter
from rich.logging import RichHandler
from rich.console import Console
from rich.theme import Theme
import logging

from ETS2LA.Utils.translator import Translate
from ETS2LA.Utils.Console.colors import *
import ETS2LA.Utils.settings as settings

import os

# Disable logging from 'comtypes', a dependency of 'pyttsx3'
logging.getLogger('comtypes').setLevel(logging.CRITICAL)

# Enables / Disables the fancy rich traceback
ft = settings.Get("global", "use_fancy_traceback", True)
USE_FANCY_TRACEBACK = True if ft is None else bool(ft)

console = Console(
    theme=Theme({
        "repr.ipv4": f"dim",
        "repr.ipv6": f"dim",
    })
)

def setup_global_logging(write_file: bool = True) -> logging.Logger:
    """
    Setup the main logger.
    
    :param bool write_file: Whether to write the logs to a file.
    :return: main logger.
    """

    # logging.DEBUG is missing since we don't want the log files
    # to have this format.
    logging.addLevelName(logging.INFO, f"{DARK_GREEN}[INF]{END}")
    logging.addLevelName(logging.WARNING, f"{DARK_YELLOW}[WRN]{END}")
    logging.addLevelName(logging.ERROR, f"{DARK_RED}[ERR]{END}")
    logging.addLevelName(logging.CRITICAL, f"{RED}[CRT]{END}")

    # Set up logging
    logging.basicConfig(format=
                            f'%(asctime)s  %(message)s',
                            level=logging.INFO,
                            datefmt=f'%H:%M:%S',
                            handlers=[RichHandler(markup=True, 
                                                  rich_tracebacks=USE_FANCY_TRACEBACK, 
                                                  show_level=True, 
                                                  show_path=True,
                                                  show_time=False,
                                                  console=console)]
                        )
    
    
    
    # File writer
    if write_file:
        if not os.path.exists("logs"):
            os.makedirs("logs")
        else:
            for file in os.listdir("logs"):
                if file.endswith(".log"):
                    try:
                        os.remove(f"logs/{file}")
                    except:
                        logging.error(f"Another ETS2LA instance is running. Please close it and try again.")
                        
        file_handler = logging.FileHandler("logs/ETS2LA.log", encoding="utf-8")
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        logging.getLogger().addHandler(file_handler)
    
    logging.info(Translate("logging.logger_initialized"))
    
    return logging.getLogger()

# Disable rich formatting for tracebacks
# when not using fancy output.
class CustomHighligher(Highlighter):
    def highlight(self, text): # type: ignore # Overrides method in Highlighter
        super().highlight(text)
        plain = text.plain
        try:
            defaultText, traceback = plain.split("Traceback (most recent call last):")
        except:
            defaultText = plain
            traceback = plain
        print(traceback.strip())
        text.plain = defaultText
        return text

def setup_process_logging(name: str, 
                          console_level = logging.INFO, 
                          filepath:str = "") -> logging.Logger:
    """
    Setup plugin logging.
    
    :param str name: The name of the plugin
    :param int console_level: The console log level (default: INFO)
    :param str filepath: The path to write the logs to (default: "")
    
    :return: plugin logger.
    """

    # Remove the default handler
    logging.getLogger().handlers = []
    logging.getLogger().addHandler(logging.NullHandler())
    logging.getLogger().setLevel(logging.DEBUG)
    
    # logging.DEBUG is missing since we don't want the log files
    # to have this format.
    logging.addLevelName(logging.INFO, f"{DARK_GREEN}[INF]{END}")
    logging.addLevelName(logging.WARNING, f"{DARK_YELLOW}[WRN]{END}")
    logging.addLevelName(logging.ERROR, f"{DARK_RED}[ERR]{END}")
    logging.addLevelName(logging.CRITICAL, f"{RED}[CRT]{END}")

    # Set up logging
    logging.basicConfig(format=
                            f'%(asctime)s  %(message)s',
                            level=logging.DEBUG,
                            datefmt=f'%H:%M:%S',
                            handlers=[RichHandler(
                                console=console,
                                markup=True, 
                                show_path=True,
                                show_time=False,
                                rich_tracebacks=USE_FANCY_TRACEBACK, 
                                show_level=True, 
                                highlighter=None if USE_FANCY_TRACEBACK 
                                else NullHighlighter()
                            )]
                        )
    
    # Create a file handler
    if filepath != "":
        if not filepath.endswith(".log"):
            filepath += f"{name}.log"
            
        if not os.path.exists(os.path.dirname(filepath)):
            os.makedirs(os.path.dirname(filepath))

        # Clear existing logs
        if os.path.exists(filepath):
            os.remove(filepath)
        
        # File writer
        file_handler = logging.FileHandler(filepath, encoding="utf-8")
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        logging.getLogger().addHandler(file_handler)
        
    # Console handler with a higher log level
    logging.getLogger().addHandler(RichHandler(
        markup=True, 
        rich_tracebacks=USE_FANCY_TRACEBACK, 
        show_level=True, 
        level=console_level, 
        console=console,
        log_time_format="%H:%M:%S", 
        show_path=False, 
        highlighter=None if USE_FANCY_TRACEBACK else CustomHighligher()
    ))
    return logging.getLogger()