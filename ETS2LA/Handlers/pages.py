import ETS2LA.variables as variables
import importlib
import logging
import time
import sys
import os

PAGES_PATH = "Pages"
last_modified_times = {}
last_update_times = {}

def get_page_names():
    files = [f for f in os.listdir(PAGES_PATH) if os.path.isfile(os.path.join(PAGES_PATH, f)) and f.endswith(".py") and f != "__init__.py"]
    return [f[:-3] for f in files]

def page_function_call(page_name: str, function_name: str, *args, **kwargs):
    module_name = f"{PAGES_PATH}.{page_name}"
    if module_name in sys.modules:
        module = sys.modules[module_name]
    else:
        module = importlib.import_module(module_name)
        importlib.reload(module)
    
    if args == ([], {}):
        args = []
    
    page = module.Page()
    page.build()
    function = getattr(page, function_name)
    return function(*args, **kwargs)

def get_pages():
    global last_modified_times, last_update_times
    files = [f for f in os.listdir(PAGES_PATH) if os.path.isfile(os.path.join(PAGES_PATH, f))]
    pages = {}
    
    while variables.IS_UI_UPDATING:
        time.sleep(0.01)
    
    variables.IS_UI_UPDATING = True
    
    for f in files:
        if f.endswith(".py") and f != "__init__.py":
            page = None
            module = None
            
            file_path = os.path.join(PAGES_PATH, f)
            last_modified_time = os.path.getmtime(file_path)
            
            module_name = f"{PAGES_PATH}.{f[:-3]}"
            if (module_name in sys.modules and last_modified_times.get(module_name) == last_modified_time) and module_name in last_update_times and time.perf_counter() - last_update_times.get(module_name) < 10:
                module = sys.modules[module_name]
            else:
                try:
                    module = importlib.import_module(module_name)
                    importlib.reload(module)
                    last_modified_times[module_name] = last_modified_time
                    last_update_times[module_name] = time.perf_counter()
                except:
                    logging.exception(f"Failed to import module {module_name}")
                    continue
            
            page = module.Page()
            pages[page.url] = page.build()
    
    variables.IS_UI_UPDATING = False
    return pages