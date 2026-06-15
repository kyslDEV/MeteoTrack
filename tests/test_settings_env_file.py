"""Testes para leitura e gravação segura do arquivo .env."""

import os
import tempfile
import unittest
from pathlib import Path

from meteotrack.config.settings import read_env_file, write_env_file


class SettingsEnvFileTest(unittest.TestCase):
    """Protege o formato usado pela tela de Configurações."""

    def test_reads_simple_env_file(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            env_path = Path(tmp_dir) / ".env"
            env_path.write_text("DB_HOST=localhost\nAPP_AUTHOR=Kaio yuri\n", encoding="utf-8")

            values = read_env_file(env_path)

            self.assertEqual(values["DB_HOST"], "localhost")
            self.assertEqual(values["APP_AUTHOR"], "Kaio yuri")

    def test_writes_known_keys_in_stable_order(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            env_path = Path(tmp_dir) / ".env"

            write_env_file(
                env_path,
                {
                    "APP_GITHUB": "https://github.com/kaioyuri",
                    "APP_AUTHOR": "Kaio yuri",
                    "DB_DATABASE": "meteotrack",
                    "DB_PASSWORD": "",
                    "DB_USER": "root",
                    "DB_PORT": "3306",
                    "DB_HOST": "localhost",
                },
            )

            content = env_path.read_text(encoding="utf-8")

            self.assertTrue(content.startswith("DB_HOST=localhost"))
            self.assertIn("APP_AUTHOR=Kaio yuri", content)
            self.assertIn("APP_GITHUB=https://github.com/kaioyuri", content)


if __name__ == "__main__":
    unittest.main()
