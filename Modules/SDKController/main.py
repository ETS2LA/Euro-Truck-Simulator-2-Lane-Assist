from ETS2LA.Settings import GlobalSettings
from ETS2LA.Module import ETS2LAModule
import platform
import struct
import mmap
import math
import time
import os

settings = GlobalSettings()
fallback_acceleration = settings.acceleration_fallback


def update_fallback_acceleration():
    global fallback_acceleration
    fallback_acceleration = settings.acceleration_fallback


settings.listen(update_fallback_acceleration)


class SCSController:
    MEM_NAME = r"Local\SCSControls"
    INPUT_MEM_NAME = r"Local\ETS2LAPluginInput"
    SHM_FILE = "/dev/shm/SCS/SCSControls"

    _BOOL_SIZE = struct.calcsize("?")
    _FLOAT_SIZE = struct.calcsize("f")

    _initialized = False

    j_left: float = 0.0
    j_right: float = 0.0
    j_up: float = 0.0
    j_down: float = 0.0
    selectfcs: bool = False
    back: bool = False
    skip: bool = False
    scrol_up: bool = False
    scrol_dwn: bool = False
    mapzoom_in: bool = False
    mapzoom_out: bool = False
    trs_zoom_in: bool = False
    trs_zoom_out: bool = False
    joy_nav_prv: bool = False
    joy_nav_nxt: bool = False
    joy_sec_prv: bool = False
    joy_sec_nxt: bool = False
    scroll_j_x: float = 0.0
    scroll_j_y: float = 0.0
    shortcut_1: bool = False
    shortcut_2: bool = False
    shortcut_3: bool = False
    shortcut_4: bool = False
    pause: bool = False
    screenshot: bool = False
    cam1: bool = False
    cam2: bool = False
    cam3: bool = False
    cam4: bool = False
    cam5: bool = False
    cam6: bool = False
    cam7: bool = False
    cam8: bool = False
    camcycle: bool = False
    camreset: bool = False
    camrotate: bool = False
    camzoomin: bool = False
    camzoomout: bool = False
    camzoom: bool = False
    camfwd: bool = False
    camback: bool = False
    camleft: bool = False
    camright: bool = False
    camup: bool = False
    camdown: bool = False
    lookleft: bool = False
    lookright: bool = False
    camlr: bool = False
    camud: bool = False
    j_cam_lk_lr: float = 0.0
    j_cam_lk_ud: float = 0.0
    j_cam_mv_lr: float = 0.0
    j_cam_mv_ud: float = 0.0
    j_trzoom_in: float = 0.0
    j_trzoom_out: float = 0.0
    j_mappan_x: float = 0.0
    j_mappan_y: float = 0.0
    j_mapzom_in: float = 0.0
    j_mapzom_out: float = 0.0
    lookpos1: bool = False
    lookpos2: bool = False
    lookpos3: bool = False
    lookpos4: bool = False
    lookpos5: bool = False
    lookpos6: bool = False
    lookpos7: bool = False
    lookpos8: bool = False
    lookpos9: bool = False
    looksteer: bool = False
    lookblink: bool = False
    steering: float = 0.0
    aforward: float = 0.0
    abackward: float = 0.0
    clutch: float = 0.0
    activate: bool = False
    menu: bool = False
    ignitionoff: bool = False
    ignitionon: bool = False
    ignitionstrt: bool = False
    attach: bool = False
    frontsuspup: bool = False
    frontsuspdwn: bool = False
    rearsuspup: bool = False
    rearsuspdwn: bool = False
    suspreset: bool = False
    horn: bool = False
    airhorn: bool = False
    lighthorn: bool = False
    beacon: bool = False
    motorbrake: bool = False
    engbraketog: bool = False
    engbrakeup: bool = False
    engbrakedwn: bool = False
    trailerbrake: bool = False
    retarderup: bool = False
    retarderdown: bool = False
    retarder0: bool = False
    retarder1: bool = False
    retarder2: bool = False
    retarder3: bool = False
    retarder4: bool = False
    retarder5: bool = False
    liftaxle: bool = False
    liftaxlet: bool = False
    slideaxlefwd: bool = False
    slideaxlebwd: bool = False
    slideaxleman: bool = False
    diflock: bool = False
    rwinopen: bool = False
    rwinclose: bool = False
    lwinopen: bool = False
    lwinclose: bool = False
    engbrakeauto: bool = False
    retarderauto: bool = False
    embrake: bool = False
    laneassmode: bool = False
    tranpwrmode: bool = False
    parkingbrake: bool = False
    wipers: bool = False
    wipersback: bool = False
    wipers0: bool = False
    wipers1: bool = False
    wipers2: bool = False
    wipers3: bool = False
    wipers4: bool = False
    cruiectrl: bool = False
    cruiectrlinc: bool = False
    cruiectrldec: bool = False
    cruiectrlres: bool = False
    accmode: bool = False
    laneassist: bool = False
    light: bool = False
    lightoff: bool = False
    lightpark: bool = False
    lighton: bool = False
    hblight: bool = False
    lblinker: bool = False
    lblinkerh: bool = False
    rblinker: bool = False
    rblinkerh: bool = False
    flasher4way: bool = False
    showmirrors: bool = False
    showhud: bool = False
    navmap: bool = False
    photo_mode: bool = False
    quicksave: bool = False
    quickload: bool = False
    radio: bool = False
    radionext: bool = False
    radioprev: bool = False
    radioup: bool = False
    radiodown: bool = False
    display: bool = False
    quickpark: bool = False
    dashmapzoom: bool = False
    tripreset: bool = False
    sb_activate: bool = False
    sb_swap: bool = False
    infotainment: bool = False
    photores: bool = False
    photomove: bool = False
    phototake: bool = False
    photofwd: bool = False
    photobwd: bool = False
    photoleft: bool = False
    photoright: bool = False
    photoup: bool = False
    photodown: bool = False
    photorolll: bool = False
    photorollr: bool = False
    photosman: bool = False
    photo_opts: bool = False
    photosnap: bool = False
    photo_hctrl: bool = False
    photonames: bool = False
    photozoomout: bool = False
    photozoomin: bool = False
    phot_z_j_out: float = 0.0
    phot_z_j_in: float = 0.0
    album_pgup: bool = False
    album_pgdn: bool = False
    album_itup: bool = False
    album_itdn: bool = False
    album_itlf: bool = False
    album_itrg: bool = False
    album_ithm: bool = False
    album_iten: bool = False
    album_itac: bool = False
    album_itop: bool = False
    album_itdl: bool = False
    camwalk_for: bool = False
    camwalk_back: bool = False
    camwalk_righ: bool = False
    camwalk_left: bool = False
    camwalk_run: bool = False
    camwalk_jump: bool = False
    camwalk_crou: bool = False
    camwalk_lr: bool = False
    camwalk_ud: bool = False
    gearup: bool = False
    geardown: bool = False
    gear0: bool = False
    geardrive: bool = False
    gearreverse: bool = False
    gearuphint: bool = False
    geardownhint: bool = False
    transemi: bool = False
    drive: bool = False
    reverse: bool = False
    cmirrorsel: bool = False
    fmirrorsel: bool = False
    mirroryawl: bool = False
    mirroryawr: bool = False
    mirrorpitu: bool = False
    mirrorpitl: bool = False
    mirrorreset: bool = False
    quicksel1: bool = False
    quicksel2: bool = False
    quicksel3: bool = False
    quicksel4: bool = False
    quicksel5: bool = False
    quicksel6: bool = False
    quicksel7: bool = False
    quicksel8: bool = False
    mpptt: bool = False
    replayhidec: bool = False
    gearsel1on: bool = False
    gearsel1off: bool = False
    gearsel1tgl: bool = False
    gearsel2on: bool = False
    gearsel2off: bool = False
    gearsel2tgl: bool = False
    gear1: bool = False
    gear2: bool = False
    gear3: bool = False
    gear4: bool = False
    gear5: bool = False
    gear6: bool = False
    gear7: bool = False
    gear8: bool = False
    gear9: bool = False
    gear10: bool = False
    gear11: bool = False
    gear12: bool = False
    gear13: bool = False
    gear14: bool = False
    gear15: bool = False
    gear16: bool = False
    adjuster: bool = False
    advpage0: bool = False
    advpage1: bool = False
    advpage2: bool = False
    advpage3: bool = False
    advpage4: bool = False
    advpagen: bool = False
    advpagep: bool = False
    advmouse: bool = False
    advetamode: bool = False
    gar_man: bool = False
    advzoomin: bool = False
    advzoomout: bool = False
    assistact1: bool = False
    assistact2: bool = False
    assistact3: bool = False
    assistact4: bool = False
    assistact5: bool = False
    adj_seats: bool = False
    adj_mirrors: bool = False
    adj_lights: bool = False
    adj_uimirror: bool = False
    chat_act: bool = False
    quick_chat: bool = False
    cycl_zoom: bool = False
    name_tags: bool = False
    headreset: bool = False
    menustereo: bool = False

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
            try:
                self._input_buff = mmap.mmap(0, 19, self.INPUT_MEM_NAME)
            except Exception:
                self._input_buff = None
                print(
                    "WARNING: Could not find ETS2LAPlugin. Please run the SDK setup again in the settings!"
                )

        elif system == "Linux":
            try:
                self._shm_fd = open(self.SHM_FILE, "rb+")
            except Exception as e:
                raise RuntimeError(
                    "ETS2/ATS is not running (Currently game needs to be running for app to start THIS IS TEMPORARY)"
                ) from e  # Temporary "fix" to remind me that the game needs to be open, waiting for tummy to respond back on how to tell the app to stop using the sdk.
            try:
                if os.name != "nt":  # silence typeright
                    self._shm_buff = mmap.mmap(
                        self._shm_fd.fileno(),
                        length=shm_size,
                        flags=mmap.MAP_SHARED,
                        access=mmap.ACCESS_WRITE,
                    )
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

        if self._input_buff and key == "aforward" and not fallback_acceleration:
            if self._input_buff is not None:
                self._input_buff.seek(5)
                self._input_buff.write(struct.pack("f", value))
                self._input_buff.seek(9)
                self._input_buff.write(struct.pack("?", True if value != 0 else False))
                self._input_buff.seek(15)
                self._input_buff.write(struct.pack("l", math.floor(time.time())))
                self._input_buff.flush()
                return

        if self._input_buff and key == "abackward" and not fallback_acceleration:
            if self._input_buff is not None:
                self._input_buff.seek(10)
                self._input_buff.write(struct.pack("f", value))
                self._input_buff.seek(14)
                self._input_buff.write(struct.pack("?", True if value != 0 else False))
                self._input_buff.seek(15)
                self._input_buff.write(struct.pack("l", math.floor(time.time())))
                self._input_buff.flush()
                return

        if key == "steering":
            if self._input_buff:
                self._input_buff.seek(0)
                self._input_buff.write(struct.pack("f", -value))
                self._input_buff.seek(4)
                self._input_buff.write(struct.pack("?", True if value != 0 else False))
                self._input_buff.seek(15)
                self._input_buff.write(struct.pack("l", math.floor(time.time())))
                self._input_buff.flush()
                return

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

    def SCSController(self):
        return SCSController()

    def run(self):
        pass
