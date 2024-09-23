from ETS2LA.plugins.runner import PluginRunner
import mmap
import json

FILENAME: str = "YOU_NEED_TO_CALL_INITIALIZE()"
HEADER_SIZE = len(int.to_bytes(0, byteorder="big"))
runner: PluginRunner = None

"""
32 bits of data for length
"""

def Initialize():
    global FILENAME
    FILENAME = "Local/ETS2LA/memory/" + runner.plugin_name  
    print(FILENAME)
    
def WriteHeader(mmap, length):
    mmap.seek(0)
    data = length.to_bytes(HEADER_SIZE, byteorder="big")
    print(data)
    mmap[0:HEADER_SIZE] = data
    
def Write(data: dict):
    try:
        # Get the data length
        data = bytes(json.dumps(data), "utf-8")
        length = int(len(data) + HEADER_SIZE)
        
        mm = mmap.mmap(0, length, FILENAME, mmap.ACCESS_WRITE)
        WriteHeader(mm, length)
        mm[HEADER_SIZE:length] = data
        mm.close()
    except:
        print("Failed to write data to memory.")
    
def ReadHeader(mmap):
    mmap.seek(0)
    length = int.from_bytes(mmap[0:HEADER_SIZE], byteorder="big")
    return length

def Read():
    try:
        mm = mmap.mmap(0, HEADER_SIZE, FILENAME, mmap.ACCESS_READ)
        print(mm[0:HEADER_SIZE])
        length = ReadHeader(mm)
        print(length)
        mm.close()
        
        mm = mmap.mmap(0, length, FILENAME, mmap.ACCESS_READ)
        data = json.loads(mm.read(length - HEADER_SIZE).decode("utf-8"))
        mm.close()
        
        return data
    except:
        return None