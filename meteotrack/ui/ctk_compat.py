"""Camada de compatibilidade para importar a UI sem CustomTkinter instalado."""

try:
    import customtkinter as ctk
except Exception:  # pragma: no cover - usado apenas antes de instalar dependências
    import tkinter as _tk
    from tkinter import ttk as _ttk

    class _FakeCTkFont(tuple):
        """Representa uma fonte CustomTkinter usando tupla do Tkinter padrão."""

        def __new__(cls, *args, **kwargs):
            size = kwargs.get("size", args[0] if args else None)
            weight = kwargs.get("weight")
            return (size, weight)

    class _CTk(_tk.Tk):
        """Substituto mínimo para a janela principal do CustomTkinter."""

        pass

    class _CTkFrame(_tk.Frame):
        """Frame compatível com os parâmetros extras usados pelo CustomTkinter."""

        def __init__(self, master=None, corner_radius=0, fg_color=None, **kwargs):
            super().__init__(master, **kwargs)

    class _CTkToplevel(_tk.Toplevel):
        """Substituto mínimo para janelas secundárias do CustomTkinter."""

        pass

    class _CTkLabel(_tk.Label):
        """Label compatível com o parâmetro `font` do CustomTkinter."""

        def __init__(self, master=None, font=None, **kwargs):
            if font:
                kwargs["font"] = font
            super().__init__(master, **kwargs)

    class _CTkEntry(_tk.Entry):
        """Entry que usa o placeholder como valor inicial no fallback."""

        def __init__(self, master=None, placeholder_text=None, **kwargs):
            super().__init__(master, **kwargs)
            if placeholder_text:
                self.insert(0, placeholder_text)

    class _CTkButton(_tk.Button):
        """Botão padrão suficiente para testes de importação."""

        pass

    class _CTkTabview(_ttk.Notebook):
        """Notebook do ttk expondo método `add` parecido com CustomTkinter."""

        def add(self, name):
            frame = _tk.Frame(self)
            super().add(frame, text=name)
            return frame

        def set(self, name):
            for tab_id in self.tabs():
                if self.tab(tab_id, "text") == name:
                    self.select(tab_id)
                    return

    def _noop(*args, **kwargs):
        """Ignora chamadas de tema quando CustomTkinter não existe."""
        return None

    class _CtkModule:
        """Objeto que expõe nomes usados pelas telas do projeto."""

        CTk = _CTk
        CTkFrame = _CTkFrame
        CTkToplevel = _CTkToplevel
        CTkLabel = _CTkLabel
        CTkEntry = _CTkEntry
        CTkButton = _CTkButton
        CTkTabview = _CTkTabview
        CTkFont = _FakeCTkFont
        set_appearance_mode = staticmethod(_noop)
        set_default_color_theme = staticmethod(_noop)

    ctk = _CtkModule()
