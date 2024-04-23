import os

CLOSE = False
"""Whether the application should close or not. Used to trigger the close from code that is not the main thread."""
RESTART = False
"""Whether the application should restart or not. Used to trigger the restart from code that is not the main thread."""

PATH = os.path.dirname(os.path.dirname(__file__)) + "\\"
"""The path to the ETS2LA folder."""