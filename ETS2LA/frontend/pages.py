import os

PAGES_PATH = "pages"

def get_pages():
    files = [f for f in os.listdir(PAGES_PATH) if os.path.isfile(os.path.join(PAGES_PATH, f))]
    # get the urls
    pages = {}
    for f in files:
        if f.endswith(".py") and f != "__init__.py":
            module = f[:-3]
            module = __import__(f"{PAGES_PATH}.{module}", fromlist=["Page"])
            page = module.Page()
            pages[page.url] = page.build()
            
    return pages