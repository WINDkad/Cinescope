from datetime import datetime
from unittest.mock import Mock

import pytz
import requests
from pydantic import BaseModel, Field, ConfigDict

from test_services.service_what_is_today import DateTimeRequest


class WorldClockResponse(BaseModel):
    id: str = Field(alias="$id")
    currentDateTime: str
    utcOffset: str
    isDayLightSavingsTime: bool
    dayOfTheWeek: str
    timeZoneName: str
    currentFileTime: int
    ordinalDate: str
    serviceResponse: None

    model_config = ConfigDict(validate_by_name=True)

class DateTimeResponse(BaseModel):
    currentDateTime: str

class WhatIsTodayResponse(BaseModel):
    message: str

def get_worldclockap_time() -> WorldClockResponse:
    response = requests.get("http://worldclockapi.com/api/json/utc/now")
    assert response.status_code == 200, "Сервер не доступен"
    return WorldClockResponse(**response.json())

class TestTodayIsHolidayServiceAPI:
    def test_worldclockapp(self):
        world_clock_response = get_worldclockap_time()
        current_date_time = world_clock_response.currentDateTime
        print(f"Текущая дата и время: {current_date_time}")
        assert current_date_time == datetime.now(pytz.utc).strftime("%Y-%m-%dT%H:%MZ"), "Дата не совпадает"

    def test_what_is_today(self):
        world_clock_response = get_worldclockap_time()
        what_is_today_response = requests.post("http://127.0.0.1:16002/what_is_today",
                                               data=DateTimeRequest(currentDateTime=world_clock_response.currentDateTime).model_dump_json()
                                               )

        assert what_is_today_response.status_code == 200, "Удаленный сервис недоступен"
        what_is_today_data = WhatIsTodayResponse(**what_is_today_response.json())
        assert what_is_today_data.message == "Сегодня нет праздников в России", "Сегодня нет праздника!"

    def test_what_is_today_by_mock(self, mocker):
        mocker.patch(
            "test_mock_services.get_worldclockap_time",
            return_value=Mock(
            currentDateTime="2025-01-01T00:00Z"
            )
        )

        world_clock_response = get_worldclockap_time()

        what_is_today_response = requests.post("http://127.0.0.1:16002/what_is_today",
                                               data=DateTimeRequest(currentDateTime=world_clock_response.currentDateTime).model_dump_json()
                                               )

        assert what_is_today_response.status_code == 200, "Удаленный сервис недоступен"
        what_is_today_data = WhatIsTodayResponse(**what_is_today_response.json())
        assert what_is_today_data.message == "Новый год", "ДОЛЖЕН БЫТЬ НОВЫЙ ГОД!"

    def stub_get_worldclockap_time(self):
        class StubWorldClockResponse:
            def __init__(self):
                self.currentDateTime = "2025-01-07T00:00Z"

        return StubWorldClockResponse()

    def test_what_is_today_by_stub(self, monkeypatch):
        monkeypatch.setattr("test_mock_services.get_worldclockap_time", self.stub_get_worldclockap_time)

        world_clock_response = get_worldclockap_time()

        what_is_today_response = requests.post(
            "http://127.0.0.1:16002/what_is_today",
            data=DateTimeRequest(currentDateTime=world_clock_response.currentDateTime).model_dump_json()
        )

        assert what_is_today_response.status_code == 200, "Удаленный сервис недоступен"
        what_is_today_data = WhatIsTodayResponse(**what_is_today_response.json())
        assert what_is_today_data.message == "Рождество Христово", "Должено быть Рождество Христово"

    def run_wiremock_worldclockap_time(self):
        wiremock_url = "http://localhost:8080/__admin/mappings"
        mapping = {
            "request": {
                "method": "GET",
                "url": "/wire/mock/api/json/utc/now"
            },
            "response": {
                "status": 200,
                "body": '''{
                    "$id": "1",
                    "currentDateTime": "2025-03-08T00:00Z",
                    "utcOffset": "00:00",
                    "isDayLightSavingsTime": false,
                    "dayOfTheWeek": "Wednesday",
                    "timeZoneName": "UTC",
                    "currentFileTime": 1324567890123,
                    "ordinalDate": "2025-1",
                    "serviceResponse": null
                }'''
            }
        }
        response = requests.post(wiremock_url, json=mapping)
        assert response.status_code == 201, "Не удалось настроить Wiremock"


    def test_what_is_today_by_wiremock(self):
        self.run_wiremock_worldclockap_time()
        world_clock_response = requests.get("http://localhost:8080/wire/mock/api/json/utc/now")
        assert world_clock_response.status_code == 200, "Удаленный сервер недоступен"
        current_date_time = WorldClockResponse(**world_clock_response.json()).currentDateTime

        what_is_today_response = requests.post(
            "http://127.0.0.1:16002/what_is_today",
            data=DateTimeRequest(currentDateTime=current_date_time).model_dump_json()
        )

        assert what_is_today_response.status_code == 200, "Удаленный сервер недоступен"
        what_is_today_data = WhatIsTodayResponse(**what_is_today_response.json())
        assert what_is_today_data.message == "Международный женский день", "Должен быть Международный женский день"


    def get_fake_worldclockap_time(self) -> WorldClockResponse:
        response = requests.get("http://127.0.0.1:16001/fake/worldclockapi/api/json/utc/now")
        assert response.status_code == 200, "Удаленный сервис недоступен"
        return WorldClockResponse(**response.json())


    def test_fake_worldclockap(self):
        world_clock_response = self.get_fake_worldclockap_time()
        current_date_time = world_clock_response.currentDateTime
        print(f"Текущая дата и время: {current_date_time=}")

        assert current_date_time == datetime.now(pytz.utc).strftime("%Y-%m-%dT%H:%MZ"), "Дата не совпадает"

    def test_fake_what_is_today(self):
        world_clock_response = self.get_fake_worldclockap_time()
        what_is_today_response = requests.post(
            "http://127.0.0.1:16002/what_is_today",
            data=DateTimeRequest(currentDateTime=world_clock_response.currentDateTime).model_dump_json()
        )
        assert what_is_today_response.status_code == 200, "Удаленный сервис недоступен"
        what_is_today_data = WhatIsTodayResponse(**what_is_today_response.json())
        assert what_is_today_data.message == "Сегодня нет праздников в России", "Сегодня нет праздника!"