from typing import Dict, List, Any, Optional, Tuple
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

class PageManager:
    @staticmethod
    def get_page_names() -> List[str]:
        """Get list of all page module names without extensions."""
        files = [f for f in os.listdir(PAGES_PATH) 
                if os.path.isfile(os.path.join(PAGES_PATH, f)) 
                and f.endswith(".py") and f != "__init__.py"]
        return [f[:-3] for f in files]

    @staticmethod
    def get_page_object(target_url: str) -> Optional[Any]:
        """Find page object by URL."""
        for page in page_objects.values():
            if page.url == target_url:
                return page
        return None

    @staticmethod
    def page_function_call(page_name: str, function_name: str, *args, **kwargs) -> Any:
        """Call a function on a specific page."""
        if page_name not in page_objects:
            raise ValueError(f"Page {page_name} not found.")
        
        page = page_objects[page_name]
        function = getattr(page, function_name)
        variables.REFRESH_PAGES = True
        return function(*args, **kwargs)

    @staticmethod
    def acquire_ui_lock():
        """Wait until UI is not updating and acquire the lock."""
        while variables.IS_UI_UPDATING:
            time.sleep(0.01)
        variables.IS_UI_UPDATING = True

    @staticmethod
    def release_ui_lock():
        """Release UI update lock."""
        variables.IS_UI_UPDATING = False

    @classmethod
    def load_page_module(cls, filename: str) -> Tuple[Optional[Any], bool]:
        """Load or reload a page module and return (page_object, is_new)."""
        if not filename.endswith(".py") or filename == "__init__.py":
            return None, False
            
        file_path = os.path.join(PAGES_PATH, filename)
        module_name = f"{PAGES_PATH}.{filename[:-3]}"
        page_name = filename[:-3]
        last_modified_time = os.path.getmtime(file_path)
        
        # Check if module needs reloading
        modified = (module_name in sys.modules and 
                   last_modified_times.get(module_name) == last_modified_time)
        loaded = module_name in last_update_times
        needs_update = not loaded
        
        # Reuse existing module if possible
        if modified and loaded and not needs_update and page_name in page_objects:
            return page_objects[page_name], False
            
        # Load/reload module
        try:
            module = importlib.import_module(module_name)
            importlib.reload(module)
            last_modified_times[module_name] = last_modified_time
            last_update_times[module_name] = time.perf_counter()
            
            # Create page instance
            page = module.Page()
            page_objects[page_name] = page
            return page, True
        except Exception:
            logging.exception(f"Failed to import module {module_name}")
            return None, False

    @classmethod
    def get_pages(cls) -> Dict[str, Any]:
        """Get all pages as a dictionary of {url: built_page}."""
        files = [f for f in os.listdir(PAGES_PATH) if os.path.isfile(os.path.join(PAGES_PATH, f))]
        pages = {}
        
        cls.acquire_ui_lock()
        try:
            for filename in files:
                page, is_new = cls.load_page_module(filename)
                if page and is_new:
                    pages[page.url] = page.build()
                    variables.REFRESH_PAGES = True
        finally:
            cls.release_ui_lock()
            
        return pages

    @classmethod
    def get_urls(cls) -> List[str]:
        """Get URLs for all available pages."""
        files = [f for f in os.listdir(PAGES_PATH) if os.path.isfile(os.path.join(PAGES_PATH, f))]
        urls = []
        
        cls.acquire_ui_lock()
        try:
            for filename in files:
                page, _ = cls.load_page_module(filename)
                if page:
                    urls.append(page.url)
        finally:
            cls.release_ui_lock()
            
        return urls

    @classmethod
    def get_page(cls, target_url: str) -> List[Any]:
        """Get a specific page by URL."""
        files = [f for f in os.listdir(PAGES_PATH) if os.path.isfile(os.path.join(PAGES_PATH, f))]
        
        cls.acquire_ui_lock()
        try:
            for filename in files:
                page, _ = cls.load_page_module(filename)
                if page and page.url == target_url:
                    try:
                        data = page.build()
                        variables.REFRESH_PAGES = True
                        return data
                    except Exception:
                        logging.exception(f"Failed to build page {target_url}")
                        return []
        finally:
            cls.release_ui_lock()
            
        return []

def get_page_names():
    return PageManager.get_page_names()

def get_page_object(target_url: str):
    return PageManager.get_page_object(target_url)

def page_function_call(page_name: str, function_name: str, *args, **kwargs):
    return PageManager.page_function_call(page_name, function_name, *args, **kwargs)

def get_pages():
    return PageManager.get_pages()

def get_urls():
    return PageManager.get_urls()

def get_page(target_url: str):
    return PageManager.get_page(target_url)

def open_event(name: str):
    return PageManager.page_function_call(name, "open_event")
    
def close_event(name: str):
    return PageManager.page_function_call(name, "close_event")