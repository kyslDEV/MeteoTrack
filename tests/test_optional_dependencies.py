"""Testes que protegem a importação sem dependências externas instaladas."""

import importlib
import unittest


class OptionalDependenciesTest(unittest.TestCase):
    """Garante que diagnóstico e testes unitários não dependam de MySQL/API/UI."""

    def test_core_modules_import_without_external_dependencies_installed(self):
        """Importar módulos principais não deve exigir pacotes opcionais imediatamente."""
        modules = [
            "meteotrack.main",
            "meteotrack.database.connection",
            "meteotrack.repositories.weather_repository",
            "meteotrack.services.open_meteo_service",
            "meteotrack.ui.app",
            "meteotrack.ui.charts_screen",
        ]

        for module_name in modules:
            with self.subTest(module=module_name):
                importlib.import_module(module_name)

    def test_diagnostics_reports_missing_dependencies(self):
        """O diagnóstico deve listar dependências sem quebrar se alguma estiver ausente."""
        diagnostics = importlib.import_module("meteotrack.diagnostics")

        result = diagnostics.collect_diagnostics()

        self.assertIn("python", result)
        self.assertIn("dependencies", result)
        self.assertIn("customtkinter", result["dependencies"])
        self.assertIn("mysql-connector-python", result["dependencies"])
        self.assertIn("requests", result["dependencies"])
        self.assertIn("matplotlib", result["dependencies"])


if __name__ == "__main__":
    unittest.main()
