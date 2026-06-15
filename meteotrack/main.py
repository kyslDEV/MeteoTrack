"""Ponto de entrada do aplicativo desktop MeteoTrack."""

import sys
from pathlib import Path


# Permite executar tanto `python -m meteotrack.main` quanto `python meteotrack/main.py`.
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from meteotrack.ui.app import App


def main() -> None:
    """Inicializa a janela principal e entrega o controle ao loop do Tk."""
    app = App()
    app.mainloop()


if __name__ == "__main__":
    main()
