"""Conexão MySQL e criação idempotente da estrutura de dados."""

from contextlib import contextmanager

from meteotrack.config.settings import DatabaseSettings


# Schema mínimo da V1. A chave única impede duplicidade por cidade, estado e data.
CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS weather_records (
    id INT AUTO_INCREMENT PRIMARY KEY,
    city VARCHAR(100) NOT NULL,
    state VARCHAR(10) NOT NULL,
    country VARCHAR(80) NOT NULL,
    record_date DATE NOT NULL,
    temp_min DECIMAL(5,2) NOT NULL,
    temp_max DECIMAL(5,2) NOT NULL,
    temp_mean DECIMAL(5,2) NOT NULL,
    classification VARCHAR(20) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY uq_weather_city_state_date (city, state, record_date)
);
"""


def _load_mysql_connector():
    """Carrega o conector MySQL somente quando uma operação de banco for usada."""
    try:
        import mysql.connector as mysql_connector
        from mysql.connector import Error
    except ModuleNotFoundError as exc:
        raise RuntimeError(
            "Dependência ausente: mysql-connector-python. "
            "Execute: pip install -r requirements.txt"
        ) from exc

    return mysql_connector, Error


class DatabaseConnection:
    """Wrapper simples para abrir conexões e preparar o banco da aplicação."""

    def __init__(self, settings: DatabaseSettings):
        self.settings = settings

    def ensure_database(self) -> None:
        """Cria o banco se ele ainda não existir."""
        mysql_connector, mysql_error = _load_mysql_connector()
        connection = None
        cursor = None
        try:
            connection = mysql_connector.connect(
                host=self.settings.host,
                port=self.settings.port,
                user=self.settings.user,
                password=self.settings.password,
            )
            cursor = connection.cursor()
            cursor.execute(
                f"CREATE DATABASE IF NOT EXISTS `{self.settings.database}` "
                "CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
            )
            connection.commit()
        except mysql_error as exc:
            raise RuntimeError(f"Erro ao preparar o banco MySQL: {exc}") from exc
        finally:
            if cursor:
                cursor.close()
            if connection and connection.is_connected():
                connection.close()

    @contextmanager
    def connect(self):
        """Abre uma conexão e garante fechamento ao final do bloco `with`."""
        mysql_connector, mysql_error = _load_mysql_connector()
        connection = None
        try:
            connection = mysql_connector.connect(
                host=self.settings.host,
                port=self.settings.port,
                user=self.settings.user,
                password=self.settings.password,
                database=self.settings.database,
            )
            yield connection
        except mysql_error as exc:
            raise RuntimeError(f"Erro de conexão com o MySQL: {exc}") from exc
        finally:
            if connection and connection.is_connected():
                connection.close()

    def initialize_schema(self) -> None:
        """Prepara banco e tabela antes de a UI tentar listar ou salvar dados."""
        self.ensure_database()
        with self.connect() as connection:
            cursor = connection.cursor()
            try:
                cursor.execute(CREATE_TABLE_SQL)
                connection.commit()
            finally:
                cursor.close()
