"""Tela inicial com as condições climáticas atuais e previsão de chuva."""

from meteotrack.models.weather_record import CurrentWeather
from meteotrack.ui.ctk_compat import ctk


class DashboardScreen(ctk.CTkFrame):
    """Mantém a primeira tela limpa, focada em tempo real."""

    def __init__(self, master, on_open_settings):
        super().__init__(master, fg_color="transparent")
        self.pack(fill="both", expand=True, padx=16, pady=16)
        self.on_open_settings = on_open_settings
        self.grid_columnconfigure(0, weight=1)
        self.current_container = ctk.CTkFrame(self)
        self.current_container.grid(row=0, column=0, sticky="ew")
        self.current_container.grid_columnconfigure((0, 1, 2, 3), weight=1)

    def render_empty(self, message: str) -> None:
        """Mantém erros técnicos fora do Dashboard."""
        return

    def render_records(self, records) -> None:
        """Histórico não aparece na tela inicial para não poluir o tempo atual."""
        return

    def render_current_loading(self) -> None:
        """Informa que os dados atuais ainda estão sendo buscados."""
        self._clear(self.current_container)
        ctk.CTkLabel(
            self.current_container,
            text="Carregando tempo atual de Caldas Novas...",
            anchor="w",
        ).grid(row=0, column=0, columnspan=4, sticky="ew", padx=16, pady=16)

    def render_current_error(self, message: str) -> None:
        """Mostra erro curto e oferece caminho para a tela técnica."""
        self._clear(self.current_container)
        ctk.CTkLabel(
            self.current_container,
            text="Não foi possível carregar o tempo atual.",
            font=ctk.CTkFont(size=18, weight="bold"),
            anchor="w",
        ).grid(row=0, column=0, columnspan=4, sticky="ew", padx=16, pady=(16, 8))
        ctk.CTkButton(
            self.current_container,
            text="Abrir configurações",
            command=self.on_open_settings,
        ).grid(row=1, column=0, sticky="w", padx=16, pady=(0, 16))

    def render_current_weather(self, current: CurrentWeather) -> None:
        """Renderiza apenas os dados climáticos que importam na abertura."""
        self._clear(self.current_container)
        ctk.CTkLabel(
            self.current_container,
            text=f"Caldas Novas agora - {current.description}",
            font=ctk.CTkFont(size=20, weight="bold"),
            anchor="w",
        ).grid(row=0, column=0, columnspan=4, sticky="ew", padx=16, pady=(16, 8))

        cards = [
            ("Temperatura", f"{current.temperature:.1f} °C"),
            ("Sensação", f"{current.apparent_temperature:.1f} °C"),
            ("Umidade", f"{current.humidity:.0f}%"),
            ("Vento", f"{current.wind_speed:.1f} km/h"),
            ("Vai chover?", "Sim" if current.will_rain else "Não"),
            ("Chance de chuva", f"{current.rain_probability:.0f}%"),
            ("Chuva prevista", f"{current.expected_precipitation:.1f} mm"),
            ("Agora", f"{current.precipitation:.1f} mm"),
        ]
        for index, (label, value) in enumerate(cards):
            row = 1 + index // 4
            column = index % 4
            self._render_card(row=row, column=column, label=label, value=value)

        ctk.CTkLabel(
            self.current_container,
            text=f"{current.rain_message} | Atualizado em: {current.observed_at}",
            anchor="w",
        ).grid(row=3, column=0, columnspan=4, sticky="ew", padx=16, pady=(4, 16))

    def _render_card(self, row: int, column: int, label: str, value: str) -> None:
        """Cria um cartão compacto para uma métrica climática."""
        card = ctk.CTkFrame(self.current_container)
        card.grid(row=row, column=column, sticky="nsew", padx=8, pady=8)
        ctk.CTkLabel(card, text=label, anchor="w").pack(fill="x", padx=16, pady=(14, 4))
        ctk.CTkLabel(card, text=value, font=ctk.CTkFont(size=20, weight="bold")).pack(
            fill="x", padx=16, pady=(0, 14)
        )

    @staticmethod
    def _clear(parent) -> None:
        """Remove widgets anteriores antes de redesenhar."""
        for widget in parent.winfo_children():
            widget.destroy()
