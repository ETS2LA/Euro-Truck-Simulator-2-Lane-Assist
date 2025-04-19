import importlib
import os

def resolve_function_from_path(path):
    module_path, _, func_path = path.rpartition(".")
    module = importlib.import_module(module_path)

    obj = module
    for attr in func_path.split("."):
        obj = getattr(obj, attr)

    return obj