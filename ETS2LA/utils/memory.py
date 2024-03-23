import mmap
import random

count = 0
def CreateSharedMemoryFile(object, id=-1):
    global count
    size = object.__sizeof__() + 1
    if id == -1:
        id = count
        count += 1
    print(size)
    shm = mmap.mmap(id, size)
    # Add the object to the shared memory
    shm.write(object)
    
    return {"mem": id, "size": size, "objectType": type(object)}

def ReplaceDataInSharedMemoryFile(memory_object_info, object):
    if type(memory_object_info) == dict:
        name = memory_object_info["mem"]
        size = memory_object_info["size"]
        
    shm = mmap.mmap(name, size)
    # Replace the data in the shared memory
    shm.seek(0)
    shm.write(object)
    return shm

def CloseSharedMemoryFile(shm):
    shm.close()
    return
    