# ruff: noqa

import os
import sys

parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..")).replace(
    "\\ETS2LA", ""
)
sys.path.insert(0, parent_dir)
os.chdir(parent_dir)

from ETS2LA.Utils.translator import generate_translations

generate_translations()
