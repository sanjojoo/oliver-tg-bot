import json
import os

DB_FILE = "users.json"

# Загрузка базы
if os.path.exists(DB_FILE):
    with open(DB_FILE, "r", encoding="utf-8") as f:
        USERS = json.load(f)
else:
    USERS = {}

# Функции для сохранения
def save_db():
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(USERS, f, indent=4, ensure_ascii=False)
