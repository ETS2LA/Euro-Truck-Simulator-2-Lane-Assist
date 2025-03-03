import logging

# Create a logger to silence httpx
logging.getLogger("httpx").setLevel(logging.WARNING)

try:
    import umami

    umami.set_url_base("https://umami.ets2la.com")
    umami.set_website_id("ca602362-299b-4222-9ea5-bbd2610488b3")
    umami.set_hostname("app.ets2la.com")
except:
    umami = None
    logging.warning("Failed to import umami.")

def TriggerEvent(event: str, data: dict | None = None):
    try:
        if umami:
            if data is None or type(data) is not dict:
                umami.new_event(
                    event_name=event,
                )
            else:
                umami.new_event(
                    event_name=event,
                    custom_data=data   
                )
    except:
        pass