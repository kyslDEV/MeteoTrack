"""Tela de coleta: valida datas, consulta API e salva no MySQL."""

from datetime import date, datetime
import threading

from meteotrack.ui.ctk_compat import ctk


class CollectScreen(ctk.CTkFrame):
    """Formulário de entrada para buscar temperaturas por intervalo."""

    def __init__(self, master, open_meteo_service, repository, on_finished, set_status):
        super().__init__(master, fg_color="transparent")
        self.pack(fill="both", expand=True, padx=16, pady=16)

        self.open_meteo_service = open_meteo_service
        self.repository = repository
        self.on_finished = on_finished
        self.set_status = set_status

        self.grid_columnconfigure(0, weight=1)
        self._build()

    def _build(self) -> None:
        """Constrói os campos de data e o botão de coleta."""
        form = ctk.CTkFrame(self)
        form.grid(row=0, column=0, sticky="ew")
        form.grid_columnconfigure((0, 1, 2), weight=1)

        ctk.CTkLabel(form, text="Data inicial (AAAA-MM-DD)").grid(
            row=0, column=0, sticky="w", padx=16, pady=(16, 4)
        )
        self.start_entry = ctk.CTkEntry(form, placeholder_text="2026-01-01")
        self.start_entry.grid(row=1, column=0, sticky="ew", padx=16, pady=(0, 16))

        ctk.CTkLabel(form, text="Data final (AAAA-MM-DD)").grid(
            row=0, column=1, sticky="w", padx=16, pady=(16, 4)
        )
        self.end_entry = ctk.CTkEntry(form, placeholder_text=date.today().isoformat())
        self.end_entry.grid(row=1, column=1, sticky="ew", padx=16, pady=(0, 16))

        self.collect_button = ctk.CTkButton(form, text="Consultar e salvar", command=self.collect)
        self.collect_button.grid(row=1, column=2, sticky="ew", padx=16, pady=(0, 16))

        info = (
            "Fonte: Open-Meteo Historical Weather API. "
            "Cidade fixa: Caldas Novas - GO, Brasil."
        )
        ctk.CTkLabel(self, text=info, anchor="w").grid(row=1, column=0, sticky="ew", pady=16)

    def collect(self) -> None:
        """Valida o intervalo informado e inicia a coleta em segundo plano."""
        try:
            start_date = datetime.strptime(self.start_entry.get().strip(), "%Y-%m-%d").date()
            end_date = datetime.strptime(self.end_entry.get().strip(), "%Y-%m-%d").date()
        except ValueError:
            self.set_status("Informe as datas no formato AAAA-MM-DD.")
            return

        if start_date > end_date:
            self.set_status("A data inicial não pode ser maior que a data final.")
            return

        self.collect_button.configure(state="disabled", text="Coletando...")
        self.set_status("Consultando Open-Meteo e salvando no MySQL...")
        # Thread evita congelar a janela durante rede e gravação no banco.
        threading.Thread(target=self._collect_worker, args=(start_date, end_date), daemon=True).start()

    def _collect_worker(self, start_date: date, end_date: date) -> None:
        """Executa consulta e persistência fora da thread principal da UI."""
        try:
            records = self.open_meteo_service.fetch_daily_temperatures(start_date, end_date)
            affected_rows = self.repository.save_many(records)
            message = f"Coleta concluída: {len(records)} dia(s) processado(s), {affected_rows} linha(s) afetada(s)."
            self.after(0, lambda: self.set_status(message))
            self.after(0, self.on_finished)
        except RuntimeError as exc:
            self.after(0, lambda: self.set_status(str(exc)))
        finally:
            self.after(0, lambda: self.collect_button.configure(state="normal", text="Consultar e salvar"))
