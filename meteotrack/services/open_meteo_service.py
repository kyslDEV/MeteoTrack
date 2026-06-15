"""Cliente da Open-Meteo para clima histórico, tempo atual e previsão de chuva."""

from datetime import date, datetime, timedelta

from meteotrack.config.settings import CitySettings
from meteotrack.models.weather_record import CurrentWeather, WeatherRecord
from meteotrack.services.weather_analysis_service import WeatherAnalysisService


RAIN_FORECAST_HOURS = 12
RAIN_PROBABILITY_THRESHOLD = 40
RAIN_PRECIPITATION_THRESHOLD = 0.1
LOCAL_GRID_CELL_SELECTION = "nearest"


def _load_requests():
    """Carrega requests apenas quando uma consulta HTTP for executada."""
    try:
        import requests
    except ModuleNotFoundError as exc:
        raise RuntimeError(
            "Dependência ausente: requests. Execute: pip install -r requirements.txt"
        ) from exc

    return requests


WEATHER_CODE_DESCRIPTIONS = {
    0: "Céu limpo",
    1: "Predominantemente limpo",
    2: "Parcialmente nublado",
    3: "Nublado",
    45: "Nevoeiro",
    48: "Nevoeiro com geada",
    51: "Garoa leve",
    53: "Garoa moderada",
    55: "Garoa intensa",
    61: "Chuva leve",
    63: "Chuva moderada",
    65: "Chuva forte",
    80: "Pancadas leves",
    81: "Pancadas moderadas",
    82: "Pancadas fortes",
    95: "Trovoadas",
}


class OpenMeteoService:
    """Busca temperaturas diárias, condições atuais e previsão de chuva."""

    HISTORICAL_URL = "https://archive-api.open-meteo.com/v1/archive"
    FORECAST_URL = "https://api.open-meteo.com/v1/forecast"

    def __init__(self, city_settings: CitySettings):
        self.city_settings = city_settings

    def fetch_daily_temperatures(self, start_date: date, end_date: date) -> list[WeatherRecord]:
        """Consulta a API histórica usando cidade fixa e intervalo informado."""
        requests = _load_requests()
        params = {
            "latitude": self.city_settings.latitude,
            "longitude": self.city_settings.longitude,
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "daily": "temperature_2m_min,temperature_2m_max,temperature_2m_mean",
            "timezone": self.city_settings.timezone,
            "cell_selection": LOCAL_GRID_CELL_SELECTION,
        }

        try:
            response = requests.get(self.HISTORICAL_URL, params=params, timeout=30)
            response.raise_for_status()
            payload = response.json()
        except requests.RequestException as exc:
            raise RuntimeError(f"Erro ao consultar a Open-Meteo: {exc}") from exc

        return self.records_from_payload(payload)

    def fetch_current_weather(self) -> CurrentWeather:
        """Consulta tempo atual e previsão de chuva das próximas horas."""
        requests = _load_requests()
        params = {
            "latitude": self.city_settings.latitude,
            "longitude": self.city_settings.longitude,
            "current": (
                "temperature_2m,relative_humidity_2m,apparent_temperature,"
                "precipitation,weather_code,wind_speed_10m"
            ),
            "hourly": "precipitation_probability,precipitation",
            "forecast_days": 1,
            "timezone": self.city_settings.timezone,
            "cell_selection": LOCAL_GRID_CELL_SELECTION,
        }

        try:
            response = requests.get(self.FORECAST_URL, params=params, timeout=20)
            response.raise_for_status()
            payload = response.json()
        except requests.RequestException as exc:
            raise RuntimeError(f"Erro ao consultar dados atuais da Open-Meteo: {exc}") from exc

        return self.current_weather_from_payload(payload)

    def records_from_payload(self, payload: dict) -> list[WeatherRecord]:
        """Converte o JSON histórico da Open-Meteo em objetos `WeatherRecord`."""
        daily = payload.get("daily") or {}
        dates = daily.get("time") or []
        mins = daily.get("temperature_2m_min") or []
        maxs = daily.get("temperature_2m_max") or []
        means = daily.get("temperature_2m_mean") or []

        if not (len(dates) == len(mins) == len(maxs) == len(means)):
            raise RuntimeError("Resposta da Open-Meteo incompleta ou inconsistente.")

        records: list[WeatherRecord] = []
        for index, record_date in enumerate(dates):
            temp_mean = float(means[index])
            # A classificação é definida no momento da conversão para manter o dado pronto.
            records.append(
                WeatherRecord(
                    city=self.city_settings.city,
                    state=self.city_settings.state,
                    country=self.city_settings.country,
                    record_date=record_date,
                    temp_min=float(mins[index]),
                    temp_max=float(maxs[index]),
                    temp_mean=temp_mean,
                    classification=WeatherAnalysisService.classify_day(temp_mean),
                )
            )
        return records

    def current_weather_from_payload(self, payload: dict) -> CurrentWeather:
        """Converte tempo atual e dados horários em modelo usado no Dashboard."""
        current = payload.get("current") or {}
        required_fields = [
            "time",
            "temperature_2m",
            "relative_humidity_2m",
            "apparent_temperature",
            "precipitation",
            "wind_speed_10m",
            "weather_code",
        ]
        missing = [field for field in required_fields if field not in current]
        if missing:
            raise RuntimeError(f"Resposta atual da Open-Meteo incompleta: {', '.join(missing)}.")

        rain_probability, expected_precipitation = self._rain_forecast_from_payload(payload, str(current["time"]))
        will_rain = (
            rain_probability >= RAIN_PROBABILITY_THRESHOLD
            or expected_precipitation > RAIN_PRECIPITATION_THRESHOLD
        )
        rain_message = (
            f"Sim, pode chover nas próximas {RAIN_FORECAST_HOURS}h"
            if will_rain
            else f"Não deve chover nas próximas {RAIN_FORECAST_HOURS}h"
        )

        weather_code = int(current["weather_code"])
        return CurrentWeather(
            observed_at=str(current["time"]),
            temperature=float(current["temperature_2m"]),
            humidity=float(current["relative_humidity_2m"]),
            apparent_temperature=float(current["apparent_temperature"]),
            precipitation=float(current["precipitation"]),
            wind_speed=float(current["wind_speed_10m"]),
            weather_code=weather_code,
            description=WEATHER_CODE_DESCRIPTIONS.get(weather_code, f"Código {weather_code}"),
            will_rain=will_rain,
            rain_probability=rain_probability,
            expected_precipitation=expected_precipitation,
            rain_message=rain_message,
        )

    def _rain_forecast_from_payload(self, payload: dict, observed_at: str) -> tuple[float, float]:
        """Resume chance máxima e volume previsto nas próximas 12 horas."""
        hourly = payload.get("hourly") or {}
        times = hourly.get("time") or []
        probabilities = hourly.get("precipitation_probability") or []
        precipitation = hourly.get("precipitation") or []

        if not (len(times) == len(probabilities) == len(precipitation)):
            return 0.0, 0.0

        start = datetime.fromisoformat(observed_at)
        end = start + timedelta(hours=RAIN_FORECAST_HOURS)
        selected_probabilities: list[float] = []
        selected_precipitation: list[float] = []

        for index, raw_time in enumerate(times):
            forecast_time = datetime.fromisoformat(str(raw_time))
            if start <= forecast_time <= end:
                selected_probabilities.append(float(probabilities[index] or 0))
                selected_precipitation.append(float(precipitation[index] or 0))

        if not selected_probabilities:
            return 0.0, 0.0

        return max(selected_probabilities), sum(selected_precipitation)
