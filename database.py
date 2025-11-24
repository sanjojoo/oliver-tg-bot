# database.py

import json
import os

DB_FILE = "users.json"

# username -> { "role": "...", "desc": "...", "banner": "banners/xxx.jpg" }
USERS = {}


def load_db():
    """Загрузить базу пользователей из файла."""
    global USERS
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r", encoding="utf-8") as f:
            USERS = json.load(f)
    else:
        USERS = {}


def save_db():
    """Сохранить базу пользователей в файл."""
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(USERS, f, indent=4, ensure_ascii=False)


# Загружаем базу при импорте модуля
load_db()
