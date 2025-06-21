import importlib
import os

def resolve_function_from_path(path):
    module_path, _, func_path = path.rpartition(".")
    print(f"Current working directory: {os.getcwd()}")
    print(f"Resolving function from path: {path}")
    print(f"Module path: {module_path}")
    print(f"Function path: {func_path}")
    module = importlib.import_module(module_path)

    obj = module
    for attr in func_path.split("."):
        obj = getattr(obj, attr)

    return obj