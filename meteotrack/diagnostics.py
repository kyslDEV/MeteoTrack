"""Diagnóstico local para testar ambiente antes de abrir a interface."""

from importlib import metadata, util
import platform

from meteotrack.config.settings import BASE_DIR, get_settings


# Cada item mapeia: nome exibido -> (nome de importação, nome do pacote pip).
DEPENDENCIES = {
    "customtkinter": ("customtkinter", "customtkinter"),
    "matplotlib": ("matplotlib", "matplotlib"),
    "mysql-connector-python": ("mysql.connector", "mysql-connector-python"),
    "python-dotenv": ("dotenv", "python-dotenv"),
    "requests": ("requests", "requests"),
}


def _dependency_status(import_name: str, package_name: str) -> dict:
    """Verifica se uma dependência opcional está disponível sem importá-la de fato."""
    try:
        installed = util.find_spec(import_name) is not None
    except ModuleNotFoundError:
        installed = False

    version = None
    if installed:
        try:
            version = metadata.version(package_name)
        except metadata.PackageNotFoundError:
            version = "desconhecida"

    return {
        "installed": installed,
        "version": version,
    }


def collect_diagnostics() -> dict:
    """Coleta informações úteis para entender falhas de instalação/configuração."""
    settings = get_settings()
    return {
        "python": platform.python_version(),
        "base_dir": str(BASE_DIR),
        "env_file_exists": (BASE_DIR / ".env").exists(),
        "author": settings.author,
        "github": settings.github,
        "database": {
            "host": settings.database.host,
            "port": settings.database.port,
            "user": settings.database.user,
            "database": settings.database.database,
            "password_configured": bool(settings.database.password),
        },
        "dependencies": {
            name: _dependency_status(import_name, package_name)
            for name, (import_name, package_name) in DEPENDENCIES.items()
        },
    }


def main() -> None:
    """Imprime um relatório simples para execução via `python -m meteotrack.diagnostics`."""
    diagnostics = collect_diagnostics()
    print("MeteoTrack - diagnóstico local")
    print(f"Python: {diagnostics['python']}")
    print(f"Pasta base: {diagnostics['base_dir']}")
    print(f"Arquivo .env: {'encontrado' if diagnostics['env_file_exists'] else 'não encontrado'}")
    print(f"Autor: {diagnostics['author']}")
    print(f"GitHub: {diagnostics['github'] or 'não configurado'}")

    database = diagnostics["database"]
    print(
        "MySQL: "
        f"{database['user']}@{database['host']}:{database['port']}/"
        f"{database['database']} "
        f"(senha {'configurada' if database['password_configured'] else 'vazia'})"
    )

    print("Dependências:")
    for name, status in diagnostics["dependencies"].items():
        if status["installed"]:
            print(f"  OK      {name} ({status['version']})")
        else:
            print(f"  FALTA   {name}")

    missing = [
        name
        for name, status in diagnostics["dependencies"].items()
        if not status["installed"]
    ]
    if missing:
        print("\nInstale as dependências com: pip install -r requirements.txt")


if __name__ == "__main__":
    main()
