"""Tela de histórico em formato de tabela."""

import tkinter as tk
from tkinter import ttk

from meteotrack.models.weather_record import WeatherRecord
from meteotrack.ui.ctk_compat import ctk


class HistoryScreen(ctk.CTkFrame):
    """Lista todos os registros salvos no MySQL."""

    def __init__(self, master):
        super().__init__(master, fg_color="transparent")
        self.pack(fill="both", expand=True, padx=16, pady=16)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self._build_table()

    def _build_table(self) -> None:
        """Cria a tabela com rolagem vertical."""
        container = ctk.CTkFrame(self)
        container.grid(row=0, column=0, sticky="nsew")
        container.grid_columnconfigure(0, weight=1)
        container.grid_rowconfigure(0, weight=1)

        columns = ("date", "min", "max", "mean", "classification")
        self.table = ttk.Treeview(container, columns=columns, show="headings", height=18)
        self.table.heading("date", text="Data")
        self.table.heading("min", text="Temp. mín")
        self.table.heading("max", text="Temp. máx")
        self.table.heading("mean", text="Temp. média")
        self.table.heading("classification", text="Classificação")

        self.table.column("date", anchor="center", width=120)
        self.table.column("min", anchor="center", width=120)
        self.table.column("max", anchor="center", width=120)
        self.table.column("mean", anchor="center", width=120)
        self.table.column("classification", anchor="center", width=140)

        scrollbar = ttk.Scrollbar(container, orient=tk.VERTICAL, command=self.table.yview)
        self.table.configure(yscrollcommand=scrollbar.set)
        self.table.grid(row=0, column=0, sticky="nsew", padx=(12, 0), pady=12)
        scrollbar.grid(row=0, column=1, sticky="ns", pady=12, padx=(0, 12))

    def render_records(self, records: list[WeatherRecord]) -> None:
        """Limpa a tabela e insere a lista atual de registros."""
        for item in self.table.get_children():
            self.table.delete(item)

        for record in records:
            self.table.insert(
                "",
                tk.END,
                values=(
                    record.record_date,
                    f"{record.temp_min:.2f} °C",
                    f"{record.temp_max:.2f} °C",
                    f"{record.temp_mean:.2f} °C",
                    record.classification,
                ),
            )
