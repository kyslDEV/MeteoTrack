"""Testes da conversão dos dados atuais retornados pela Open-Meteo."""

import unittest

from meteotrack.config.settings import CitySettings
from meteotrack.services.open_meteo_service import OpenMeteoService


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


if __name__ == "__main__":
    unittest.main()
