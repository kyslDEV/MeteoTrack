"""Janela principal do MeteoTrack e composição das telas."""

import threading

from meteotrack.config.settings import get_settings
from meteotrack.database.connection import DatabaseConnection
from meteotrack.repositories.weather_repository import WeatherRepository
from meteotrack.services.open_meteo_service import OpenMeteoService
from meteotrack.ui.charts_screen import ChartsScreen
from meteotrack.ui.collect_screen import CollectScreen
from meteotrack.ui.ctk_compat import ctk
from meteotrack.ui.dashboard_screen import DashboardScreen
from meteotrack.ui.history_screen import HistoryScreen
from meteotrack.ui.settings_screen import SettingsScreen
from meteotrack.ui.splash_screen import SplashScreen


class App(ctk.CTk):
    """Orquestra abas, splash, serviços e revalidação de configuração."""

    def __init__(self):
        super().__init__()
        ctk.set_appearance_mode("System")
        ctk.set_default_color_theme("blue")

        self.settings = get_settings()
        self.repository = None
        self.open_meteo_service = None
        self.db_ready = False
        self.splash = None

        self._configure_services()

        self.title("MeteoTrack v0.1")
        self.geometry("1120x720")
        self.minsize(960, 640)
        self.withdraw()

        self._build_layout()
        self._show_splash()
        self.after(1800, self._finish_startup)

    def _configure_services(self) -> None:
        """Recria serviços sempre que o .env for alterado."""
        self.settings = get_settings()
        self.repository = WeatherRepository(DatabaseConnection(self.settings.database))
        self.open_meteo_service = OpenMeteoService(self.settings.city)

    def _show_splash(self) -> None:
        """Exibe a tela temporária com autor e GitHub."""
        self.splash = SplashScreen(
            self,
            author=self.settings.author,
            github=self.settings.github,
        )
        self.splash.lift()
        self.splash.focus_force()

    def _finish_startup(self) -> None:
        """Fecha a splash, mostra a janela principal e carrega dados iniciais."""
        if self.splash is not None:
            self.splash.destroy()
            self.splash = None

        self.deiconify()
        self.revalidate_environment()
        self.refresh_current_weather()

    def _build_layout(self) -> None:
        """Monta cabeçalho, botão de configuração e abas principais."""
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        header = ctk.CTkFrame(self, corner_radius=0)
        header.grid(row=0, column=0, sticky="ew")
        header.grid_columnconfigure(0, weight=1)

        title = ctk.CTkLabel(
            header,
            text="MeteoTrack v0.1 - Caldas Novas, GO",
            font=ctk.CTkFont(size=22, weight="bold"),
        )
        title.grid(row=0, column=0, sticky="w", padx=20, pady=(14, 2))

        ctk.CTkButton(
            header,
            text="Configurações",
            command=self.show_settings,
        ).grid(row=0, column=1, sticky="e", padx=20, pady=(14, 2))

        self.status_label = ctk.CTkLabel(header, text="Inicializando...", anchor="w")
        self.status_label.grid(row=1, column=0, columnspan=2, sticky="ew", padx=20, pady=(0, 12))

        self.tabs = ctk.CTkTabview(self)
        self.tabs.grid(row=1, column=0, sticky="nsew", padx=16, pady=16)

        dashboard_tab = self.tabs.add("Dashboard")
        collect_tab = self.tabs.add("Coleta")
        history_tab = self.tabs.add("Histórico")
        charts_tab = self.tabs.add("Gráfico")
        settings_tab = self.tabs.add("Configurações")

        self.dashboard_screen = DashboardScreen(dashboard_tab, on_open_settings=self.show_settings)
        self.collect_screen = CollectScreen(
            collect_tab,
            open_meteo_service=self.open_meteo_service,
            repository=self.repository,
            on_finished=self.refresh_data,
            set_status=self.set_status,
        )
        self.history_screen = HistoryScreen(history_tab)
        self.charts_screen = ChartsScreen(charts_tab)
        self.settings_screen = SettingsScreen(
            settings_tab,
            on_save=self.on_settings_saved,
            on_revalidate=self.revalidate_environment,
            set_status=self.set_status,
        )

    def show_settings(self) -> None:
        """Leva o usuário para a aba técnica de Configurações."""
        self.tabs.set("Configurações")

    def on_settings_saved(self) -> None:
        """Recarrega serviços e telas depois que o .env é salvo."""
        self._configure_services()
        self.collect_screen.open_meteo_service = self.open_meteo_service
        self.collect_screen.repository = self.repository
        self.revalidate_environment()
        self.refresh_current_weather()

    def revalidate_environment(self) -> None:
        """Valida MySQL e atualiza apenas telas técnicas/histórico."""
        try:
            self.repository.initialize()
            self.db_ready = True
            self.set_status("Ambiente validado.")
            self.settings_screen.set_database_status("conectado e estrutura verificada.")
        except RuntimeError as exc:
            self.db_ready = False
            self.set_status("Banco não conectado. Ajuste em Configurações.")
            self.settings_screen.set_database_status(str(exc))

        self.refresh_data()
        self.settings_screen.render_diagnostics()

    def set_status(self, message: str) -> None:
        """Atualiza a barra de status global com mensagens curtas."""
        self.status_label.configure(text=message)

    def refresh_current_weather(self) -> None:
        """Busca os dados atuais sem congelar a interface."""
        self.dashboard_screen.render_current_loading()
        threading.Thread(target=self._current_weather_worker, daemon=True).start()

    def _current_weather_worker(self) -> None:
        """Consulta condições atuais fora da thread principal da UI."""
        try:
            current = self.open_meteo_service.fetch_current_weather()
            self.after(0, lambda: self.dashboard_screen.render_current_weather(current))
        except RuntimeError:
            self.after(
                0,
                lambda: self.dashboard_screen.render_current_error(
                    "Falha ao consultar a Open-Meteo. Veja Configurações."
                ),
            )

    def refresh_data(self) -> None:
        """Atualiza histórico e gráfico; o Dashboard permanece focado no tempo atual."""
        if not self.db_ready:
            self.history_screen.render_records([])
            self.charts_screen.render_chart([])
            return

        try:
            records = self.repository.list_all()
            self.history_screen.render_records(records)
            self.charts_screen.render_chart(records)
        except RuntimeError as exc:
            self.settings_screen.set_database_status(str(exc))
