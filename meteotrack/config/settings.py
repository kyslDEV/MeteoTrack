"""Carrega e grava as configurações locais do MeteoTrack."""

from dataclasses import dataclass
from pathlib import Path
import os

try:
    from dotenv import load_dotenv  # type: ignore
except Exception:
    # Fallback leve para diagnóstico/configuração antes de instalar python-dotenv.
    def load_dotenv(path=None, override=False):
        if path is None:
            return False
        for key, value in read_env_file(Path(path)).items():
            if override or key not in os.environ:
                os.environ[key] = value
        return True


BASE_DIR = Path(__file__).resolve().parents[2]
ENV_PATH = BASE_DIR / ".env"

ENV_KEYS = [
    "DB_HOST",
    "DB_PORT",
    "DB_USER",
    "DB_PASSWORD",
    "DB_DATABASE",
    "APP_AUTHOR",
    "APP_GITHUB",
]


@dataclass(frozen=True)
class CitySettings:
    """Dados fixos de Caldas Novas usados em todas as consultas da V1."""

    city: str = "Caldas Novas"
    state: str = "GO"
    country: str = "Brasil"
    latitude: float = -17.7452
    longitude: float = -48.6253
    timezone: str = "America/Sao_Paulo"


@dataclass(frozen=True)
class DatabaseSettings:
    """Credenciais e destino do banco MySQL."""

    host: str
    port: int
    user: str
    password: str
    database: str


@dataclass(frozen=True)
class AppSettings:
    """Agrupa as configurações consumidas pela aplicação."""

    city: CitySettings
    database: DatabaseSettings
    author: str
    github: str


def read_env_file(path: Path = ENV_PATH) -> dict[str, str]:
    """Lê um arquivo .env simples no formato KEY=VALUE."""
    values: dict[str, str] = {}
    if not path.exists():
        return values

    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key.strip()] = value.strip().strip('"').strip("'")
    return values


def write_env_file(path: Path, values: dict[str, str]) -> None:
    """Grava as configurações conhecidas em ordem estável."""
    merged = read_env_file(path)
    merged.update({key: str(value) for key, value in values.items()})

    lines = [f"{key}={merged.get(key, '')}" for key in ENV_KEYS]
    extra_keys = sorted(key for key in merged if key not in ENV_KEYS)
    lines.extend(f"{key}={merged[key]}" for key in extra_keys)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def get_settings() -> AppSettings:
    """Monta as configurações finais, relendo o .env a cada chamada."""
    load_dotenv(ENV_PATH, override=True)
    return AppSettings(
        city=CitySettings(),
        database=DatabaseSettings(
            host=os.getenv("DB_HOST", "localhost"),
            port=int(os.getenv("DB_PORT", "3306")),
            user=os.getenv("DB_USER", "root"),
            password=os.getenv("DB_PASSWORD", ""),
            database=os.getenv("DB_DATABASE", "meteotrack"),
        ),
        author=os.getenv("APP_AUTHOR", "Kaio yuri"),
        github=os.getenv("APP_GITHUB", ""),
    )
