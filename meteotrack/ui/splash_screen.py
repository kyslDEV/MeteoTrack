"""Splash screen exibida antes da janela principal."""

from meteotrack.ui.ctk_compat import ctk


class SplashScreen(ctk.CTkToplevel):
    """Janela temporária com identificação do sistema, autor e GitHub."""

    def __init__(self, master, author: str, github: str = ""):
        super().__init__(master)
        self.title("MeteoTrack")
        self.geometry("440x260")
        self.resizable(False, False)

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure((0, 1, 2, 3), weight=1)

        ctk.CTkLabel(
            self,
            text="MeteoTrack",
            font=ctk.CTkFont(size=30, weight="bold"),
        ).grid(row=0, column=0, sticky="s", padx=24, pady=(28, 4))

        ctk.CTkLabel(
            self,
            text="Monitoramento climático de Caldas Novas - GO",
            font=ctk.CTkFont(size=14),
        ).grid(row=1, column=0, sticky="n", padx=24)

        ctk.CTkLabel(
            self,
            text=f"Autor: {author}",
            font=ctk.CTkFont(size=15, weight="bold"),
        ).grid(row=2, column=0, sticky="n", padx=24, pady=(0, 4))

        github_text = github if github else "GitHub: configure na aba Configurações"
        ctk.CTkLabel(self, text=github_text).grid(
            row=3, column=0, sticky="n", padx=24, pady=(0, 24)
        )

        self._center_on_screen()

    def _center_on_screen(self) -> None:
        """Centraliza a splash usando as dimensões disponíveis do monitor."""
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = int((self.winfo_screenwidth() - width) / 2)
        y = int((self.winfo_screenheight() - height) / 2)
        self.geometry(f"{width}x{height}+{x}+{y}")
