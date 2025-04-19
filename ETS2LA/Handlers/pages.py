import ETS2LA.variables as variables
import importlib
import logging
import time
import sys
import os

PAGES_PATH = "Pages"
page_objects = {}
last_modified_times = {}
last_update_times = {}

def get_page_names():
    files = [f for f in os.listdir(PAGES_PATH) if os.path.isfile(os.path.join(PAGES_PATH, f)) and f.endswith(".py") and f != "__init__.py"]
    return [f[:-3] for f in files]

def get_page_object(target_url: str):
    for page in page_objects.values():
        if page.url == target_url:
            return page

def page_function_call(page_name: str, function_name: str, *args, **kwargs):
    print(page_objects)
    if page_name not in page_objects:
        raise ValueError(f"Page {page_name} not found.")
    
    page = page_objects[page_name]
    function = getattr(page, function_name)
    variables.REFRESH_PAGES = True
    return function(*args, **kwargs)

def get_pages():
    global last_modified_times, last_update_times, page_objects
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
            
            modified = module_name in sys.modules and last_modified_times.get(module_name) == last_modified_time
            loaded = module_name in last_update_times
            needs_update = time.perf_counter() - last_update_times.get(module_name) < 10 # type: ignore     

            if modified and loaded and not needs_update:
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
            
            if module_name.split(".")[-1] in page_objects and modified and loaded:
                page = page_objects[module_name.split(".")[-1]]
            else:
                page = module.Page()
                pages[page.url] = page.build()
                variables.REFRESH_PAGES = True
                page_objects[module_name.split(".")[-1]] = page
    
    variables.IS_UI_UPDATING = False
    return pages

def get_urls():
    global last_modified_times, last_update_times, page_objects
    files = [f for f in os.listdir(PAGES_PATH) if os.path.isfile(os.path.join(PAGES_PATH, f))]
    urls = []
    
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
            
            modified = module_name in sys.modules and last_modified_times.get(module_name) == last_modified_time
            loaded = module_name in last_update_times

            if modified and loaded: # ensure all are loaded
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
            
            if module_name.split(".")[-1] in page_objects and modified and loaded:
                page = page_objects[module_name.split(".")[-1]]
            else:
                page = module.Page()
                page_objects[module_name.split(".")[-1]] = page

            urls.append(page.url)
    
    variables.IS_UI_UPDATING = False
    return urls

def get_page(target_url: str):
    global last_modified_times, last_update_times, page_objects
    files = [f for f in os.listdir(PAGES_PATH) if os.path.isfile(os.path.join(PAGES_PATH, f))]
    page = []
    
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
            
            modified = module_name in sys.modules and last_modified_times.get(module_name) == last_modified_time
            loaded = module_name in last_update_times  

            if modified and loaded: # ensure all are loaded
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
            
            if module_name.split(".")[-1] in page_objects and modified and loaded:
                page = page_objects[module_name.split(".")[-1]]
            else:
                page = module.Page()
                page_objects[module_name.split(".")[-1]] = page

            if page.url == target_url:
                try:
                    data = page.build()
                    variables.REFRESH_PAGES = True
                except:
                    logging.exception(f"Failed to build page {target_url}")
                    data = []
                    
                variables.IS_UI_UPDATING = False
                return data
    
    variables.IS_UI_UPDATING = False
    return []
