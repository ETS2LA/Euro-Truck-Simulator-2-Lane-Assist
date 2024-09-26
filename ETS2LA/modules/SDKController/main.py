import numpy as np
import platform
import struct
import mmap
import sys
import cv2
import os

from typing import Dict


# https://docs.python.org/3/whatsnew/3.7.html
# the insertion-order preservation nature of dict objects has
# been declared to be an official part of the Python language spec.
assert sys.version_info >= (3, 7)

runner = None

def Initialize():
    pass # Do nothing

class SCSController:
    MEM_NAME = r"Local\SCSControls"
    SHM_FILE = "/dev/shm/SCS/SCSControls"

    _BOOL_SIZE = struct.calcsize("?")
    _FLOAT_SIZE = struct.calcsize("f")

    _initialized = False

    steering: float = 0.0
    aforward: float = 0.0
    abackward: float = 0.0
    clutch: float = 0.0
    pause: bool = False
    parkingbrake: bool = False
    wipers: bool = False
    cruiectrl: bool = False
    cruiectrlinc: bool = False
    cruiectrldec: bool = False
    cruiectrlres: bool = False
    light: bool = False
    hblight: bool = False
    lblinker: bool = False
    rblinker: bool = False
    quickpark: bool = False
    drive: bool = False
    reverse: bool = False
    cycl_zoom: bool = False
    tripreset: bool = False
    wipersback: bool = False
    wipers0: bool = False
    wipers1: bool = False
    wipers2: bool = False
    wipers3: bool = False
    wipers4: bool = False
    horn: bool = False
    airhorn: bool = False
    lighthorn: bool = False
    cam1: bool = False
    cam2: bool = False
    cam3: bool = False
    cam4: bool = False
    cam5: bool = False
    cam6: bool = False
    cam7: bool = False
    cam8: bool = False
    mapzoom_in: bool = False
    mapzoom_out: bool = False
    accmode: bool = False
    showmirrors: bool = False
    flasher4way: bool = False
    activate: bool = False
    assistact1: bool = False
    assistact2: bool = False
    assistact3: bool = False
    assistact4: bool = False
    assistact5: bool = False

    def __init__(self):
        shm_size = 0
        self._shm_offsets: Dict[str, int] = {}
        for i, t in SCSController.__annotations__.items():
            self._shm_offsets[i] = shm_size

            if t is bool:
                shm_size += self._BOOL_SIZE
            elif t is float:
                shm_size += self._FLOAT_SIZE

        system = platform.system()
        if system == "Windows":
            self._shm_buff = mmap.mmap(0, shm_size, self.MEM_NAME)
        elif system == "Linux":
            try:
                self._shm_fd = open(self.SHM_FILE, "rb+")
            except:
                raise RuntimeError(f"ETS2/ATS is not running (Currently game needs to be running for app to start (Blame tummy not me :3))") #Temporary "fix" to remind me that the game needs to be open, waiting for tummy to respond back on how to tell the app to stop using the sdk.
            try:
                self._shm_buff = mmap.mmap(self._shm_fd.fileno(), length=shm_size,
                                           flags=mmap.MAP_SHARED, access=mmap.ACCESS_WRITE)
            except Exception as e:
                self._shm_fd.close()
                raise e
        else:
            raise RuntimeError(f"{system} is not supported")

        self._initialized = True

    def close(self):
        self._shm_buff.close()
        self._shm_fd.close()

    def reset(self):
        for i, t in SCSController.__annotations__.items():
            if t is bool:
                self._shm_buff.seek(self._shm_offsets[i])
                self._shm_buff.write(struct.pack("?", False))
            elif t is float:
                self._shm_buff.seek(self._shm_offsets[i])
                self._shm_buff.write(struct.pack("f", 0.0))

        self._shm_buff.flush()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def __getattribute__(self, key):
        if key not in SCSController.__annotations__:
            return super().__getattribute__(key)

        self._shm_buff.seek(self._shm_offsets[key])
        expected_type = SCSController.__annotations__[key]
        if expected_type is bool:
            return struct.unpack("?", self._shm_buff.read(self._BOOL_SIZE))[0]
        elif expected_type is float:
            return struct.unpack("f", self._shm_buff.read(self._FLOAT_SIZE))[0]
        else:
            raise RuntimeError(f"'{expected_type}' type is unknown")

    def __setattr__(self, key, value):
        if not self._initialized:
            return super().__setattr__(key, value)

        if key not in SCSController.__annotations__:
            raise AttributeError(f"'{key}' input is not known")

        value_type = type(value)
        expected_type = SCSController.__annotations__[key]
        if value_type is not expected_type:
            raise TypeError(f"'{key}' must be of type '{expected_type}'")

        self._shm_buff.seek(self._shm_offsets[key])
        if value_type is bool:
            self._shm_buff.write(struct.pack("?", value))
        elif value_type is float:
            self._shm_buff.write(struct.pack("f", value))
        else:
            raise TypeError(f"'{value_type}' type is not supported")

        self._shm_buff.flush()