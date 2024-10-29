import time

# https://stackoverflow.com/a/60185893
def AccurateSleep(duration, get_now=time.perf_counter):
    """
    NOTE: USE THIS SPARINGLY, AS THIS CAN BE RESOURCE INTENSIVE.
    
    Will sleep for the given duration. This function is more accurate than the standard time.sleep function.

    Args:
        duration (float): Seconds to sleep.
        get_now (float, optional): Current time. Defaults to time.perf_counter.
    """
    now = get_now()
    end = now + duration
    while now < end:
        now = get_now()