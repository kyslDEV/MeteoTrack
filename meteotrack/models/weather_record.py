"""Modelos de dados usados entre API, banco, análise e interface."""

from dataclasses import dataclass


@dataclass(frozen=True)
class WeatherRecord:
    """Representa um dia de medição de temperatura para a cidade monitorada."""

    record_date: str
    temp_min: float
    temp_max: float
    temp_mean: float
    city: str = "Caldas Novas"
    state: str = "GO"
    country: str = "Brasil"
    classification: str = ""


@dataclass(frozen=True)
class WeatherSummary:
    """Resumo estatístico exibido nas telas de análise."""

    total_days: int
    coldest_day: WeatherRecord | None
    hottest_day: WeatherRecord | None
    average_temperature: float | None


@dataclass(frozen=True)
class CurrentWeather:
    """Condição meteorológica atual e risco de chuva exibidos na primeira tela."""

    observed_at: str
    temperature: float
    humidity: float
    apparent_temperature: float
    precipitation: float
    wind_speed: float
    weather_code: int
    description: str
    will_rain: bool
    rain_probability: float
    expected_precipitation: float
    rain_message: str
