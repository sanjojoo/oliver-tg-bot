import telebot
from config import TOKEN, ADMIN_ID
from database import USERS, save_db
from roles import ROLES
from telebot import types

bot = telebot.TeleBot(TOKEN)


# ===== ПРОВЕРКА АДМИНА =====
def is_admin(id):
    return id == ADMIN_ID

def main_menu():
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add("✅ Профиль", "📜 Список гарантов")
    kb.add("🔎 Проверить человека", "🚫 Слить скамера")
    return kb
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
    reply_markup=main_menu()
)
    


# ===== ЧЕК ПОЛЬЗОВАТЕЛЯ =====
@bot.message_handler(func=lambda m: m.text and m.text.lower().startswith("чек"))
def check_user(message):
    try:
        username = message.text.split()[1].replace("@", "")
    except:
        return bot.send_message(message.chat.id, "⚠ Использование:\nчек @username")

    role = ROLES.get(username)

    # ===== Уникальные описания для каждой роли =====
    ROLE_TEXTS = {
        "Владелец базы": ("0%", "Человек являеться владельцем чата , ему можно доверять 🛡"),
        "Владелец": ("0%", "Человек являеться владельцем чата , ему можно доверять 🛡"),
        "Со Владелец": ("0%", "Человек являеться Со.владельцем чата , ему можно доверять 🛡"),
        "Гл.Админ": ("10%", "Человек являеться главным админом чата , уровень доверия высокий ✅"),
        "Директор": ("0%", "Человек являеться директор , можете спокойно доверять ✅"),
        "Старший гарант": ("10%", "Человек являеться старшим гарантом , можно доверять ✅"),
        "Админ": ("20%", "Человек являеться админом чата , ему можно доверять но будьте осторожны 🛡"),
        "Мл.Админ": ("25%", "Человек являеться младшим админом , рекомендуется внимательность ⚠️"),
        "Разработчик": ("0%", "Человек являеться разработчиком чата , участие подтверждено ✅")
    }

    # ===== НАЙДЕН В БАЗЕ =====
    if role in ROLE_TEXTS:
        scam_risk, trust_text = ROLE_TEXTS[role]

    else:  # ===== НЕ НАЙДЕН =====
        role = "не известен"
        scam_risk = "50%"
        trust_text = "Человека нету в базе данных AK , будьте бдительными и используйте проверенных гарантов 🔖"

    # ===== ФИНАЛЬНЫЙ ВЫВОД =====
    text = (
        f"🎭 Информация о: @{username}\n"
        f"📌 Статус: {role}\n"
        f"🌍 Страна: не известна\n\n"
        f"⚠ Риск скама: {scam_risk}\n\n"
        f"{trust_text}"
    )

    bot.send_message(message.chat.id, text)




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
        
@bot.message_handler(func=lambda m: m.text == "✅ Профиль")
def profile(message):
    bot.send_message(message.chat.id, "Ваш профиль пока в разработке ✅")


@bot.message_handler(func=lambda m: m.text == "📜 Список гарантов")
def guarantors(message):
    bot.send_message(message.chat.id,
        "📜 Список гарантов:\n\n"
        "@tgarmikk\n"
        "@laiov\n"
        "@damir"
    )


@bot.message_handler(func=lambda m: m.text == "🔎 Проверить человека")
def ask_check(message):
    bot.send_message(message.chat.id, "Введите:\nчек @username")


@bot.message_handler(func=lambda m: m.text == "🚫 Слить скамера")
def report_scammer(message):
    bot.send_message(message.chat.id,
        "🚫 Чтобы слить скамера, отправьте доказательства и username сюда:\n\n"
        "@tgarmikk"
    )



bot.polling(none_stop=True)






