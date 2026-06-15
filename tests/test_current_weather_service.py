"""Testes da conversão dos dados atuais retornados pela Open-Meteo."""

from datetime import date
import unittest
from unittest.mock import patch

from meteotrack.config.settings import CitySettings
from meteotrack.services.open_meteo_service import OpenMeteoService


class FakeResponse:
    """Resposta HTTP minima para testar parametros sem chamar a API real."""

    def __init__(self, payload):
        self.payload = payload

    def raise_for_status(self):
        return None

    def json(self):
        return self.payload


class FakeRequests:
    """Captura chamadas do servico para validar parametros enviados."""

    RequestException = RuntimeError

    def __init__(self, payload):
        self.payload = payload
        self.calls = []

    def get(self, url, params, timeout):
        self.calls.append({"url": url, "params": params, "timeout": timeout})
        return FakeResponse(self.payload)


class CurrentWeatherServiceTest(unittest.TestCase):
    """Garante que o payload `current` vire um modelo simples para a UI."""

    def test_converts_current_weather_payload(self):
        service = OpenMeteoService(CitySettings())
        payload = {
            "current": {
                "time": "2026-06-14T10:30",
                "temperature_2m": 27.4,
                "relative_humidity_2m": 62,
                "apparent_temperature": 28.1,
                "precipitation": 0.0,
                "wind_speed_10m": 11.2,
                "weather_code": 1,
            }
        }

        current = service.current_weather_from_payload(payload)

        self.assertEqual(current.observed_at, "2026-06-14T10:30")
        self.assertEqual(current.temperature, 27.4)
        self.assertEqual(current.humidity, 62)
        self.assertEqual(current.description, "Predominantemente limpo")

    def test_answers_if_it_will_rain_in_next_12_hours(self):
        service = OpenMeteoService(CitySettings())
        payload = {
            "current": {
                "time": "2026-06-14T10:00",
                "temperature_2m": 27.4,
                "relative_humidity_2m": 62,
                "apparent_temperature": 28.1,
                "precipitation": 0.0,
                "wind_speed_10m": 11.2,
                "weather_code": 2,
            },
            "hourly": {
                "time": [
                    "2026-06-14T10:00",
                    "2026-06-14T11:00",
                    "2026-06-14T12:00",
                    "2026-06-14T23:00",
                ],
                "precipitation_probability": [10, 35, 72, 90],
                "precipitation": [0.0, 0.1, 2.4, 7.0],
            },
        }

        current = service.current_weather_from_payload(payload)

        self.assertTrue(current.will_rain)
        self.assertEqual(current.rain_probability, 72)
        self.assertAlmostEqual(current.expected_precipitation, 2.5)
        self.assertEqual(current.rain_message, "Sim, pode chover nas próximas 12h")

    def test_historical_query_uses_nearest_grid_cell_for_local_precision(self):
        fake_requests = FakeRequests(
            {
                "daily": {
                    "time": ["2026-06-14"],
                    "temperature_2m_min": [18.4],
                    "temperature_2m_max": [31.7],
                    "temperature_2m_mean": [25.2],
                }
            }
        )
        service = OpenMeteoService(CitySettings())

        with patch("meteotrack.services.open_meteo_service._load_requests", return_value=fake_requests):
            service.fetch_daily_temperatures(date(2026, 6, 14), date(2026, 6, 14))

        self.assertEqual(fake_requests.calls[0]["params"]["cell_selection"], "nearest")

    def test_current_weather_query_uses_nearest_grid_cell_for_local_precision(self):
        fake_requests = FakeRequests(
            {
                "current": {
                    "time": "2026-06-14T10:30",
                    "temperature_2m": 27.4,
                    "relative_humidity_2m": 62,
                    "apparent_temperature": 28.1,
                    "precipitation": 0.0,
                    "wind_speed_10m": 11.2,
                    "weather_code": 1,
                },
                "hourly": {
                    "time": ["2026-06-14T10:00"],
                    "precipitation_probability": [0],
                    "precipitation": [0.0],
                },
            }
        )
        service = OpenMeteoService(CitySettings())

        with patch("meteotrack.services.open_meteo_service._load_requests", return_value=fake_requests):
            service.fetch_current_weather()

        self.assertEqual(fake_requests.calls[0]["params"]["cell_selection"], "nearest")


if __name__ == "__main__":
    unittest.main()
