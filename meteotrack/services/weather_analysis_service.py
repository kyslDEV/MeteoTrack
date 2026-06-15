"""Regras de negócio para classificação e resumo dos registros climáticos."""

from meteotrack.models.weather_record import WeatherRecord, WeatherSummary


class WeatherAnalysisService:
    """Centraliza cálculos para evitar duplicação entre UI, API e repositório."""

    @staticmethod
    def classify_day(temp_mean: float) -> str:
        """Classifica o dia pela temperatura média definida na especificação da V1."""
        if temp_mean < 22:
            return "Frio"
        if temp_mean <= 28:
            return "Normal"
        return "Quente"

    @staticmethod
    def calculate_summary(records: list[WeatherRecord]) -> WeatherSummary:
        """Calcula totais e extremos usados nos cartões do dashboard."""
        if not records:
            return WeatherSummary(
                total_days=0,
                coldest_day=None,
                hottest_day=None,
                average_temperature=None,
            )

        coldest_day = min(records, key=lambda record: record.temp_min)
        hottest_day = max(records, key=lambda record: record.temp_max)
        average_temperature = sum(record.temp_mean for record in records) / len(records)
        return WeatherSummary(
            total_days=len(records),
            coldest_day=coldest_day,
            hottest_day=hottest_day,
            average_temperature=average_temperature,
        )
