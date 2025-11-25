# main.py

import telebot
from telebot import types

from config import TOKEN, ADMIN_ID
from database import USERS, save_db
from roles import ROLES, ROLE_INFO, DEFAULT_ROLE

bot = telebot.TeleBot(TOKEN)


# ===== ПРОВЕРКА АДМИНА =====
def is_admin(user_id: int) -> bool:
    return user_id == ADMIN_ID


def main_menu():
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add("✅ Профиль", "📜 Список гарантов")
    kb.add("🔎 Проверить человека", "🚫 Слить скамера")
    return kb


# ===== СБОРКА И ОТПРАВКА ПРОФИЛЯ (ТЕКСТ + ФОТО, ЕСЛИ ЕСТЬ) =====
def send_profile(chat_id: int, username: str, is_self: bool = False):
    uname = username.lower()

    # 1. Берём данные из users.json (если админ что-то записал туда)
    user_data = USERS.get(uname)

    # 2. Определяем роль:
    role_name = None
    if user_data and "role" in user_data:
        role_name = user_data["role"]
    else:
        # если не в базе — пробуем взять из статического словаря ROLES
        role_name = ROLES.get(uname)

    # 3. Информация по роли
    if role_name and role_name in ROLE_INFO:
        info = ROLE_INFO[role_name]
        risk = info["risk"]
        desc = info["description"]
    elif role_name:
        risk = "20%"
        desc = f"Роль: {role_name}. Отдельного описания в системе нет, будьте внимательны ⚠️"
    else:
        role_name = DEFAULT_ROLE["name"]
        risk = DEFAULT_ROLE["risk"]
        desc = DEFAULT_ROLE["description"]

    # 4. Баннер-фото для конкретного пользователя
    banner_path = None
    if user_data and "banner" in user_data:
        banner_path = user_data["banner"]
    else:
        # если нет своего баннера – можно не отправлять фото или использовать дефолт
        banner_path = None  # или "banners/default.png", если сделаешь общий баннер

    title = "🧾 Ваш профиль" if is_self else f"🎭 Информация о: @{uname}"

    text = (
        f"{title}\n\n"
        f"👤 Ник: @{uname}\n"
        f"📌 Роль: {role_name}\n"
        f"⚠ Риск скама: {risk}\n\n"
        f"ℹ Описание:\n{desc}"
    )

    # 5. Отправляем с фото, если найден баннер
    if banner_path:
        try:
            with open(banner_path, "rb") as photo:
                bot.send_photo(chat_id, photo, caption=text)
            return
        except Exception as e:
            # Если что-то не так с фото – просто отправляем текст
            print(f"Ошибка при отправке баннера {banner_path}: {e}")

    # если баннера нет или ошибка – отправляем обычный текст
    bot.send_message(chat_id, text)


# ===== СТАРТ =====
@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(
        message.chat.id,
        "👋 Добро пожаловать в *AK Use Bot!* \n\n"
        "Этот бот поможет вам выбрать надёжного гаранта нашего чата:\n"
        "https://t.me/Currency_exchangess\n\n"
        "🔎 *Как работает бот?*\n"
        "Всё очень просто — отправьте username любого гаранта,\n"
        "а мы проверим его репутацию и предоставим вам всю необходимую информацию.\n\n"
        "Чтобы начать — просто отправьте чек @username.",
        reply_markup=main_menu(),
        parse_mode="Markdown"
    )


# ===== ЧЕК ПОЛЬЗОВАТЕЛЯ ПО КОМАНДЕ "чек @username" =====
@bot.message_handler(func=lambda m: m.text and m.text.lower().startswith("чек"))
def check_user(message):
    try:
        username = message.text.split()[1].replace("@", "")
    except Exception:
        return bot.send_message(message.chat.id, "⚠ Использование:\nчек @username")

    send_profile(message.chat.id, username, is_self=False)


# ===== АДМИН: ДОБАВИТЬ ПОЛЬЗОВАТЕЛЯ =====
@bot.message_handler(commands=['add'])
def add_user(message):
    if not is_admin(message.from_user.id):
        return bot.send_message(message.chat.id, "❌ Нет доступа.")

    try:
        _, username, role = message.text.split(maxsplit=2)
        username = username.replace("@", "").lower()
    except Exception:
        return bot.send_message(message.chat.id, "Использование: /add @user роль")

    if username not in USERS:
        USERS[username] = {}

    USERS[username]["role"] = role
    # баннер можно прописать руками в users.json или сделать отдельную команду /setbanner
    save_db()
    bot.send_message(message.chat.id, f"✅ Добавлен/обновлён @{username} как '{role}'")


# ===== АДМИН: УДАЛИТЬ ПОЛЬЗОВАТЕЛЯ =====
@bot.message_handler(commands=['del'])
def delete_user(message):
    if not is_admin(message.from_user.id):
        return bot.send_message(message.chat.id, "❌ Нет доступа.")

    try:
        _, username = message.text.split(maxsplit=1)
        username = username.replace("@", "").lower()
    except Exception:
        return bot.send_message(message.chat.id, "Использование: /del @user")

    if username in USERS:
        del USERS[username]
        save_db()
        bot.send_message(message.chat.id, f"🗑 Удалён @{username}")
    else:
        bot.send_message(message.chat.id, "❌ Нет в базе.")


# ===== АДМИН: ИЗМЕНИТЬ РОЛЬ =====
@bot.message_handler(commands=['edit'])
def edit_user(message):
    if not is_admin(message.from_user.id):
        return bot.send_message(message.chat.id, "❌ Нет доступа.")

    try:
        _, username, new_role = message.text.split(maxsplit=2)
        username = username.replace("@", "").lower()
    except Exception:
        return bot.send_message(message.chat.id, "Использование: /edit @user новая_роль")

    if username not in USERS:
        USERS[username] = {}

    USERS[username]["role"] = new_role
    save_db()
    bot.send_message(message.chat.id, f"🔄 Роль @{username} изменена на '{new_role}'")


# ===== КНОПКА "✅ Профиль" =====
@bot.message_handler(func=lambda m: m.text == "✅ Профиль")
def profile(message):
    if not message.from_user.username:
        return bot.send_message(
            message.chat.id,
            "❗ У вас не установлен username в Telegram.\n"
            "Зайдите в настройки Telegram и задайте @username."
        )

    send_profile(message.chat.id, message.from_user.username, is_self=True)


# ===== ОСТАЛЬНЫЕ КНОПКИ =====
@bot.message_handler(func=lambda m: m.text == "📜 Список гарантов")
def guarantors(message):
    bot.send_message(
        message.chat.id,
        "📜 Список гарантов:\n\n"
        "tgarmikk.t.me\n"
        "laiov.t.me\n"
        "damirbeer.t.mer"
        "@routyyy_tag"
        "@neazy_bro"
        "@Dinkie_tag"
        "@slc_usdt"
    )


@bot.message_handler(func=lambda m: m.text == "🔎 Проверить человека")
def ask_check(message):
    bot.send_message(message.chat.id, "Введите:\nчек @username")


@bot.message_handler(func=lambda m: m.text == "🚫 Слить скамера")
def report_scammer(message):
    bot.send_message(
        message.chat.id,
        "🚫 Чтобы слить скамера, отправьте доказательства и username сюда:\n\n"
        "@tgarmikk"
    )


bot.polling(none_stop=True)



