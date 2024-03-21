from typing import Union
from fastapi import FastAPI
import threading
import logging

app = FastAPI()


@app.get("/")
def read_root():
    return {"Hello": "World"}


def run():
    import uvicorn
    threading.Thread(target=uvicorn.run, args=(app,), kwargs={"port": 37520, "host": "localhost", "log_level": "critical"}, daemon=True).start()
    logging.info("Webserver started on http://localhost:37520")