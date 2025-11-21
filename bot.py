import telebot
from config import TOKEN, ADMIN_ID
from database import USERS
from database import USERS, save_db
from roles import ROLES

bot = telebot.TeleBot(TOKEN)


# ===== ПРОВЕРКА АДМИНА =====
def is_admin(id):
    return id == ADMIN_ID


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
    "Чтобы начать — просто отправьте чек @username."
)
    


# ===== ЧЕК ПОЛЬЗОВАТЕЛЯ =====
@bot.message_handler(func=lambda m: m.text.lower().startswith("чек"))
def check_user(message):
    parts = message.text.split()

    # проверяем корректность ввода
    if len(parts) < 2:
        return bot.send_message(
            message.chat.id,
            "⚠ Использование:\nчек @username"
        )

    username = parts[1].replace("@", "")

    # ищем пользователя
    role = ROLES.get(username)

    if role:
        bot.send_message(
            message.chat.id,
            f"👤 Пользователь: @{username}\n"
            f"🔰 Роль: {role}"
        )
    else:
        bot.send_message(
            message.chat.id,
            "❌ Данный человек не найден в нашей базе данных ❌\n\n"
            "Скорее всего, он не является гарантом нашего чата или может быть фейковым аккаунтом 👁‍🗨.\n\n"
            "⚠ Вероятность скама в таких случаях составляет 85% и выше ⛔️."
        )




# ===== АДМИН: ДОБАВИТЬ ПОЛЬЗОВАТЕЛЯ =====
@bot.message_handler(commands=['add'])
def add_user(message):
    if not is_admin(message.from_user.id):
        return bot.send_message(message.chat.id, "❌ Нет доступа.")

    try:
        _, username, role = message.text.split(maxsplit=2)
        username = username.replace("@", "").lower()
    except:
        return bot.send_message(message.chat.id, "Использование: /add @user роль")

    USERS[username] = {"role": role, "desc": ""}
    bot.send_message(message.chat.id, f"✅ Добавлен @{username} как '{role}'")
    USERS[username] = {"role": role, "desc": ""}
    save_db()

# ===== АДМИН: УДАЛИТЬ ПОЛЬЗОВАТЕЛЯ =====
@bot.message_handler(commands=['del'])
def delete_user(message):
    if not is_admin(message.from_user.id):
        return bot.send_message(message.chat.id, "❌ Нет доступа.")

    try:
        _, username = message.text.split(maxsplit=1)
        username = username.replace("@", "").lower()
    except:
        return bot.send_message(message.chat.id, "Использование: /del @user")
    
    if username in USERS:
        del USERS[username]
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
    except:
        return bot.send_message(message.chat.id, "Использование: /edit @user новая_роль")

    if username in USERS:
        USERS[username]["role"] = new_role
        bot.send_message(message.chat.id, f"🔄 Роль @{username} изменена на '{new_role}'")
    else:
        bot.send_message(message.chat.id, "❌ Нет в базе.")
        



bot.polling(none_stop=True)
