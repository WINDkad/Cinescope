import datetime

import pytz
from fastapi import FastAPI

app = FastAPI()

@app.get("/ping")
def ping():
    return "PONG!"

@app.get("/fake/worldclockapi/api/json/utc/now")
def get_current_utc_time():
    now = datetime.datetime.now(pytz.utc)

    response = {
        "$id": "1",
        "currentDateTime": now.strftime("%Y-%m-%dT%H:%MZ"),
        "utcOffset": "00:00:00",
        "isDayLightSavingsTime": False,
        "dayOfTheWeek": now.strftime("%A"),
        "timeZoneName": "UTC",
        "currentFileTime": int(now.timestamp() * 10 ** 7),
        "ordinalDate": now.strftime("%Y-%j"),
        "serviceResponse": None
    }
    return response

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=16001)