"""Testes das regras de negócio de classificação e resumo climático."""

import unittest

from meteotrack.models.weather_record import WeatherRecord
from meteotrack.services.weather_analysis_service import WeatherAnalysisService


class WeatherAnalysisServiceTest(unittest.TestCase):
    """Garante que regras centrais não mudem sem perceber."""

    def test_classifies_daily_temperature_ranges(self):
        """Confirma os limites exatos entre Frio, Normal e Quente."""
        self.assertEqual(WeatherAnalysisService.classify_day(21.9), "Frio")
        self.assertEqual(WeatherAnalysisService.classify_day(22.0), "Normal")
        self.assertEqual(WeatherAnalysisService.classify_day(28.0), "Normal")
        self.assertEqual(WeatherAnalysisService.classify_day(28.1), "Quente")

    def test_calculates_summary_for_records(self):
        """Confirma total, extremos e média exibidos no dashboard."""
        records = [
            WeatherRecord(record_date="2026-01-01", temp_min=18.0, temp_max=30.0, temp_mean=24.0),
            WeatherRecord(record_date="2026-01-02", temp_min=16.0, temp_max=31.0, temp_mean=23.5),
            WeatherRecord(record_date="2026-01-03", temp_min=22.0, temp_max=35.0, temp_mean=29.0),
        ]

        summary = WeatherAnalysisService.calculate_summary(records)

        self.assertEqual(summary.total_days, 3)
        self.assertEqual(summary.coldest_day.record_date, "2026-01-02")
        self.assertEqual(summary.hottest_day.record_date, "2026-01-03")
        self.assertAlmostEqual(summary.average_temperature, 25.5)


if __name__ == "__main__":
    unittest.main()
