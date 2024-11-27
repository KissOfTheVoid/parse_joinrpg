# parse_joinrpg
Скрипт для забора данных из джойна и выгрузки в файл .csv
Нужны pandas и pyyaml

дальше вам нужно сделать в корне parser_config.py структуры

auth_url: "https://joinrpg.ru/x-api/token"
login_data:
  username: "you@email.com"
  password: "your_password"
  grant_type: "password"
characters_url: "https://joinrpg.ru/x-game-api/{projectId}/characters"
character_details_url: "https://joinrpg.ru/x-game-api/{projectId}/characters/{characterId}"
project_id: ****  # Замените на ID вашего проекта
