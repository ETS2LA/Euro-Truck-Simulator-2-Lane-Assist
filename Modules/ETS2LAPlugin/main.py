from ETS2LA.Module import *
import platform
import struct
import mmap
import struct
import time

class Module(ETS2LAModule):
    def imports(self):
        global np, sys, cv2, os, Dict
        import numpy as np
        import sys
        import cv2
        import os

        from typing import Dict


        # https://docs.python.org/3/whatsnew/3.7.html
        # the insertion-order preservation nature of dict objects has
        # been declared to be an official part of the Python language spec.
        assert sys.version_info >= (3, 7)
    
    def run():
        # Open the file
        mmName = r"Local\SCSControls"

        floatCount = 1
        boolCount = 1

        # Memory map the file
        print("Waiting for memory map from game...")
        buf = None
        while buf is None:
            floatSize = floatCount * 4
            boolSize = boolCount * 1
            size = floatSize + boolSize
            buf = mmap.mmap(0, size, "Local\SCSControls")
            time.sleep(0.1)
        print("Memory map received!")

        steering = -1
        didIncrease = False
        try:
            while True:
                # Write the floats and bools to memory
                buf[:] = struct.pack('ffff15?', steering, 0.0, 0.0, 0.0,
                                    False, False, False, False,
                                    False, False, False, False,
                                    False, False, False, False,
                                    False, False, False)

                # Sleep for a while to prevent high CPU usage
                time.sleep(0.01)
                if didIncrease:
                    steering = steering - 0.005
                else:
                    steering = steering + 0.005
                if steering > 1:
                    didIncrease = True
                elif steering < -1:
                    didIncrease = False
                print(steering, end='\r')
        except:
            import traceback
            traceback.print_exc()
            pass