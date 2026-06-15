"""Tela de gráfico da temperatura média diária."""

from meteotrack.models.weather_record import WeatherRecord
from meteotrack.ui.ctk_compat import ctk


class ChartsScreen(ctk.CTkFrame):
    """Renderiza o gráfico de linha usando matplotlib quando instalado."""

    def __init__(self, master):
        super().__init__(master, fg_color="transparent")
        self.pack(fill="both", expand=True, padx=16, pady=16)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.canvas = None

    def render_chart(self, records: list[WeatherRecord]) -> None:
        """Desenha a série temporal de temperatura média."""
        for widget in self.winfo_children():
            widget.destroy()

        try:
            from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
            from matplotlib.figure import Figure
        except ModuleNotFoundError:
            ctk.CTkLabel(
                self,
                text="Instale matplotlib com: pip install -r requirements.txt",
                anchor="center",
            ).grid(row=0, column=0, sticky="nsew")
            return

        ordered_records = sorted(records, key=lambda record: record.record_date)
        figure = Figure(figsize=(9, 5), dpi=100)
        axis = figure.add_subplot(111)

        if ordered_records:
            dates = [record.record_date for record in ordered_records]
            means = [record.temp_mean for record in ordered_records]
            axis.plot(dates, means, marker="o", linewidth=2)
            axis.set_title("Temperatura média diária")
            axis.set_xlabel("Data")
            axis.set_ylabel("Temperatura média (°C)")
            axis.tick_params(axis="x", rotation=45)
            axis.grid(True, alpha=0.3)
        else:
            axis.text(0.5, 0.5, "Nenhum dado registrado", ha="center", va="center")
            axis.set_axis_off()

        figure.tight_layout()
        self.canvas = FigureCanvasTkAgg(figure, master=self)
        self.canvas.draw()
        self.canvas.get_tk_widget().grid(row=0, column=0, sticky="nsew")
