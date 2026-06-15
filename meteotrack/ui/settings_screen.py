"""Tela dedicada a configurações técnicas e diagnóstico."""

from meteotrack.config.settings import ENV_PATH, get_settings, write_env_file
from meteotrack.diagnostics import collect_diagnostics
from meteotrack.ui.ctk_compat import ctk


class SettingsScreen(ctk.CTkFrame):
    """Centraliza MySQL, autoria, GitHub e diagnósticos fora do Dashboard."""

    def __init__(self, master, on_save, on_revalidate, set_status):
        super().__init__(master, fg_color="transparent")
        self.pack(fill="both", expand=True, padx=16, pady=16)
        self.on_save = on_save
        self.on_revalidate = on_revalidate
        self.set_status = set_status
        self.entries: dict[str, ctk.CTkEntry] = {}

        self.grid_columnconfigure(0, weight=1)
        self._build()
        self.load_from_settings()
        self.render_diagnostics()

    def _build(self) -> None:
        """Monta os campos editáveis e área de diagnóstico."""
        form = ctk.CTkFrame(self)
        form.grid(row=0, column=0, sticky="ew")
        form.grid_columnconfigure((0, 1), weight=1)

        fields = [
            ("DB_HOST", "Host MySQL", False),
            ("DB_PORT", "Porta MySQL", False),
            ("DB_USER", "Usuário MySQL", False),
            ("DB_PASSWORD", "Senha MySQL", True),
            ("DB_DATABASE", "Banco de dados", False),
            ("APP_AUTHOR", "Autor", False),
            ("APP_GITHUB", "GitHub", False),
        ]

        for index, (key, label, secret) in enumerate(fields):
            row = index // 2
            column = index % 2
            field = ctk.CTkFrame(form)
            field.grid(row=row, column=column, sticky="ew", padx=12, pady=8)
            field.grid_columnconfigure(0, weight=1)
            ctk.CTkLabel(field, text=label, anchor="w").grid(row=0, column=0, sticky="ew", padx=10, pady=(8, 4))
            entry_kwargs = {"show": "*"} if secret else {}
            entry = ctk.CTkEntry(field, **entry_kwargs)
            entry.grid(row=1, column=0, sticky="ew", padx=10, pady=(0, 10))
            self.entries[key] = entry

        actions = ctk.CTkFrame(self)
        actions.grid(row=1, column=0, sticky="ew", pady=(12, 0))
        actions.grid_columnconfigure((0, 1, 2), weight=1)

        ctk.CTkButton(actions, text="Salvar configurações", command=self.save).grid(
            row=0, column=0, sticky="ew", padx=8, pady=10
        )
        ctk.CTkButton(actions, text="Testar diagnóstico", command=self.render_diagnostics).grid(
            row=0, column=1, sticky="ew", padx=8, pady=10
        )
        ctk.CTkButton(actions, text="Revalidar banco", command=self.on_revalidate).grid(
            row=0, column=2, sticky="ew", padx=8, pady=10
        )

        self.database_status = ctk.CTkLabel(self, text="", anchor="w")
        self.database_status.grid(row=2, column=0, sticky="ew", pady=(12, 4))

        self.diagnostics_label = ctk.CTkLabel(self, text="", anchor="w", justify="left")
        self.diagnostics_label.grid(row=3, column=0, sticky="ew")

    def load_from_settings(self) -> None:
        """Preenche campos com a configuração atualmente carregada."""
        settings = get_settings()
        values = {
            "DB_HOST": settings.database.host,
            "DB_PORT": str(settings.database.port),
            "DB_USER": settings.database.user,
            "DB_PASSWORD": settings.database.password,
            "DB_DATABASE": settings.database.database,
            "APP_AUTHOR": settings.author,
            "APP_GITHUB": settings.github,
        }
        for key, value in values.items():
            entry = self.entries[key]
            entry.delete(0, "end")
            entry.insert(0, value)

    def save(self) -> None:
        """Salva os campos editáveis no .env e avisa a aplicação para recarregar."""
        values = {key: entry.get().strip() for key, entry in self.entries.items()}
        write_env_file(ENV_PATH, values)
        self.set_status("Configurações salvas. Revalidando ambiente...")
        self.on_save()
        self.render_diagnostics()

    def set_database_status(self, message: str) -> None:
        """Mostra detalhes de conexão MySQL apenas nesta tela técnica."""
        self.database_status.configure(text=f"Banco: {message}")

    def render_diagnostics(self) -> None:
        """Atualiza o diagnóstico local dentro da aba de Configurações."""
        diagnostics = collect_diagnostics()
        database = diagnostics["database"]
        dependency_lines = []
        for name, status in diagnostics["dependencies"].items():
            state = "OK" if status["installed"] else "FALTA"
            version = f" ({status['version']})" if status["version"] else ""
            dependency_lines.append(f"- {name}: {state}{version}")

        text = "\n".join(
            [
                "Diagnóstico local",
                f"Python: {diagnostics['python']}",
                f".env: {'encontrado' if diagnostics['env_file_exists'] else 'não encontrado'}",
                f"MySQL: {database['user']}@{database['host']}:{database['port']}/{database['database']}",
                f"Senha MySQL: {'configurada' if database['password_configured'] else 'vazia'}",
                "Dependências:",
                *dependency_lines,
            ]
        )
        self.diagnostics_label.configure(text=text)
