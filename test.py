import requests
import time

api = "https://tracker.ets2map.com/v3/area?x1=-15487&y1=-3827&x2=-11813&y2=-8439&server=2"

lastData = None
lastDataTime = time.time()
times = []
while True:
    time.sleep(0.1)
    data = requests.get(api).json()
    if data != lastData:
        times.append(time.time() - lastDataTime)
        print(f"Update rate: {1 / (sum(times) / len(times))} Hz                               ", end="\r")
        lastDataTime = time.time()
        lastData = data