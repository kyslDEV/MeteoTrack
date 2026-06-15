"""Persistência dos registros meteorológicos no MySQL."""

from meteotrack.database.connection import DatabaseConnection
from meteotrack.models.weather_record import WeatherRecord
from meteotrack.services.weather_analysis_service import WeatherAnalysisService


class WeatherRepository:
    """Camada que traduz objetos `WeatherRecord` para SQL e vice-versa."""

    def __init__(self, db: DatabaseConnection):
        self.db = db

    def initialize(self) -> None:
        """Delega a preparação do schema para a conexão de banco."""
        self.db.initialize_schema()

    def save_many(self, records: list[WeatherRecord]) -> int:
        """Insere ou atualiza registros, mantendo um único registro por data."""
        if not records:
            return 0

        # ON DUPLICATE KEY UPDATE torna a coleta repetível sem criar linhas duplicadas.
        sql = """
        INSERT INTO weather_records
            (city, state, country, record_date, temp_min, temp_max, temp_mean, classification)
        VALUES
            (%s, %s, %s, %s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
            country = VALUES(country),
            temp_min = VALUES(temp_min),
            temp_max = VALUES(temp_max),
            temp_mean = VALUES(temp_mean),
            classification = VALUES(classification),
            updated_at = CURRENT_TIMESTAMP
        """
        # A classificação é recalculada se o objeto vier sem esse campo preenchido.
        values = [
            (
                record.city,
                record.state,
                record.country,
                record.record_date,
                record.temp_min,
                record.temp_max,
                record.temp_mean,
                record.classification or WeatherAnalysisService.classify_day(record.temp_mean),
            )
            for record in records
        ]

        with self.db.connect() as connection:
            cursor = connection.cursor()
            try:
                cursor.executemany(sql, values)
                connection.commit()
                return cursor.rowcount
            finally:
                cursor.close()

    def list_all(self) -> list[WeatherRecord]:
        """Retorna o histórico mais recente primeiro para facilitar leitura na tabela."""
        sql = """
        SELECT city, state, country, record_date, temp_min, temp_max, temp_mean, classification
        FROM weather_records
        ORDER BY record_date DESC
        """
        with self.db.connect() as connection:
            cursor = connection.cursor(dictionary=True)
            try:
                cursor.execute(sql)
                rows = cursor.fetchall()
            finally:
                cursor.close()

        # MySQL retorna Decimal/date; a UI trabalha com float/string para renderização.
        return [
            WeatherRecord(
                city=row["city"],
                state=row["state"],
                country=row["country"],
                record_date=row["record_date"].isoformat(),
                temp_min=float(row["temp_min"]),
                temp_max=float(row["temp_max"]),
                temp_mean=float(row["temp_mean"]),
                classification=row["classification"],
            )
            for row in rows
        ]
