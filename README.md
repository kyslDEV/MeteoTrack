# MeteoTrack v0.1

Sistema desktop em Python para registrar, consultar e analisar temperaturas de Caldas Novas - GO usando Open-Meteo e MySQL.

## Funcionalidades

- Tela inicial limpa com tempo atual de Caldas Novas.
- Consulta histórica por data inicial e data final.
- Coleta das variáveis `temperature_2m_min`, `temperature_2m_max` e `temperature_2m_mean`.
- Persistência em MySQL com prevenção de duplicidade por cidade, estado e data.
- Histórico em tabela.
- Gráfico de linha da temperatura média diária com matplotlib.
- Splash screen com autor e GitHub configurável.
- Aba Configurações para MySQL, autoria, GitHub e diagnóstico local.
- Classificação diária:
  - `temp_mean < 22`: Frio
  - `22 <= temp_mean <= 28`: Normal
  - `temp_mean > 28`: Quente

## Cidade Fixa

- Cidade: Caldas Novas
- Estado: GO
- País: Brasil
- Latitude: -17.7452
- Longitude: -48.6253
- Timezone: America/Sao_Paulo

## Instalação

```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## Configuração

O arquivo `.env` controla banco, autor e GitHub:

```env
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=
DB_DATABASE=meteotrack
APP_AUTHOR=Kaio yuri
APP_GITHUB=
```

Esses campos também podem ser editados na aba **Configurações** dentro do sistema.

## Diagnóstico

Antes de abrir a interface, rode:

```powershell
python -m meteotrack.diagnostics
```

Esse comando mostra Python, `.env`, autoria, GitHub, configuração MySQL e dependências.

## Banco de Dados

Ao iniciar, o app tenta criar o banco e a tabela automaticamente. O usuário MySQL precisa ter permissão para `CREATE DATABASE` e `CREATE TABLE`.

Se preferir criar manualmente:

```powershell
mysql -u root -p < meteotrack/database/schema.sql
```

## Execução

```powershell
python -m meteotrack.main
```

## Testes

```powershell
python -m unittest discover -s tests
```

## Estrutura

```text
meteotrack/
|-- main.py
|-- diagnostics.py
|-- config/
|   `-- settings.py
|-- database/
|   |-- connection.py
|   `-- schema.sql
|-- models/
|   `-- weather_record.py
|-- services/
|   |-- open_meteo_service.py
|   `-- weather_analysis_service.py
|-- repositories/
|   `-- weather_repository.py
`-- ui/
    |-- app.py
    |-- ctk_compat.py
    |-- dashboard_screen.py
    |-- settings_screen.py
    |-- collect_screen.py
    |-- history_screen.py
    `-- charts_screen.py
```

## Resumo das Alterações

- Dashboard foi limpo para mostrar apenas dados climáticos atuais.
- Erros e diagnósticos técnicos foram movidos para a aba Configurações.
- Autor padrão ajustado para `Kaio yuri`.
- Campo `APP_GITHUB` foi adicionado ao `.env` e à tela de Configurações.
