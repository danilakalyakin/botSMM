import telebot
from telebot import types
from flask import Flask, request
import json
import os
import threading

# 🔹 Токен бота
TOKEN = "7990097395:AAEKXo3sP-bu32bfVSscCI26aFmoibLcm5Y"
bot = telebot.TeleBot(TOKEN)

# 🔹 Ник администратора
admin_username = "danilkalyakin"

# 🔹 Файл для хранения заявок
APPLICATIONS_FILE = "applications.json"

# 🔹 Храним ID сообщений для возможной очистки
user_messages = {}

# ---------- ПАНЕЛЬ ----------
def get_main_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("📚 Кейсы", "👨‍🏫 Тарифы")
    markup.add("📞 Поддержка", "🧹 Очистить чат")
    markup.add("ℹ️ О боте", "📝 Оставить заявку")
    return markup

# ---------- START ----------
@bot.message_handler(commands=['start'])
def start(message):
    msg = bot.send_message(
        message.chat.id,
        "👋 Привет! Я — бот SMM агенства SHISH PROMOTION. Выбери действие ниже:",
        reply_markup=get_main_menu()
    )
    save_message(message.chat.id, msg.message_id)

# ---------- ТЕКСТ ----------
@bot.message_handler(content_types=['text'])
def handle_text(message):
    if message.text == "📚 Кейсы":
        send_cases(message)
    elif message.text == "👨‍🏫 Тарифы":
        send_tariffs(message)
    elif message.text == "📞 Поддержка":
        send_support_link(message)
    elif message.text == "🧹 Очистить чат":
        clear_chat(message)
    elif message.text == "ℹ️ О боте":
        show_about(message)
    elif message.text == "📝 Оставить заявку":
        start_application(message)
    else:
        msg = bot.send_message(message.chat.id, "Я не понимаю эту команду 😅", reply_markup=get_main_menu())
        save_message(message.chat.id, msg.message_id)

# ---------- КЕЙСЫ ----------
def send_cases(message):
    cases = [
        {"title": "Кейс 1", "desc": "Пример кейса №1 — описание проекта.", "link": f"https://t.me/{admin_username}"},
        {"title": "Кейс 2", "desc": "Пример кейса №2 — результаты работы.", "link": f"https://t.me/{admin_username}"},
        {"title": "Кейс 3", "desc": "Пример кейса №3 — кейс из реальной практики.", "link": f"https://t.me/{admin_username}"}
    ]
    for c in cases:
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("✉️ Связаться", url=c["link"]))
        text = f"📘 <b>{c['title']}</b>\n\n{c['desc']}"
        msg = bot.send_message(message.chat.id, text, parse_mode="HTML", reply_markup=markup)
        save_message(message.chat.id, msg.message_id)

# ---------- ТАРИФЫ ----------
def send_tariffs(message):
    tariffs = [
        {"name": "Elementary", "price": "25 000₽", "desc": "Базовый уровень"},
        {"name": "Average", "price": "45 000₽", "desc": "Оптимальный вариант"},
        {"name": "PRO", "price": "75 000₽", "desc": "Максимальный уровень"}
    ]
    for t in tariffs:
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton(f"Подробнее ({t['name']})", callback_data=f"tariff_{t['name']}"))
        text = f"💼 <b>{t['name']}</b> — {t['price']}\n{t['desc']}"
        msg = bot.send_message(message.chat.id, text, parse_mode="HTML", reply_markup=markup)
        save_message(message.chat.id, msg.message_id)

# ---------- ПОДДЕРЖКА ----------
def send_support_link(message):
    link = f"https://t.me/{admin_username}"
    msg = bot.send_message(message.chat.id, f"📞 Связаться с администратором можно здесь: {link}", reply_markup=get_main_menu())
    save_message(message.chat.id, msg.message_id)

# ---------- ОЧИСТКА ЧАТА ----------
def clear_chat(message):
    chat_id = message.chat.id
    if chat_id in user_messages:
        for msg_id in user_messages[chat_id]:
            try:
                bot.delete_message(chat_id, msg_id)
            except:
                pass
        user_messages[chat_id] = []

    final_msg = bot.send_message(chat_id, "✅ Чат очищен!", reply_markup=get_main_menu())
    save_message(chat_id, final_msg.message_id)

# ---------- О БОТЕ ----------
def show_about(message):
    text = f"""
🤖 <b>О боте</b>

Этот бот помогает пользователям получать информацию о:
📚 Кейсы — примеры наших проектов  
👨‍🏫 Тарифы — варианты сотрудничества  
📞 Поддержка — связь с менеджером  

Администратор на связи: <b>Danila Kalyakin</b>  
Контакт: https://t.me/{admin_username}
"""
    msg = bot.send_message(message.chat.id, text, parse_mode="HTML", reply_markup=get_main_menu())
    save_message(message.chat.id, msg.message_id)

# ---------- ЗАЯВКА ----------
def start_application(message):
    chat_id = message.chat.id
    msg = bot.send_message(chat_id, "📝 Введите ваше имя и интересующий тариф:", reply_markup=types.ReplyKeyboardRemove())
    save_message(chat_id, msg.message_id)
    bot.register_next_step_handler(msg, get_application_name)

def get_application_name(message):
    chat_id = message.chat.id
    name = message.text
    msg = bot.send_message(chat_id, "📱 Введите ваш номер телефона:", reply_markup=types.ReplyKeyboardRemove())
    save_message(chat_id, msg.message_id)
    bot.register_next_step_handler(msg, get_application_phone, name)

def get_application_phone(message, name):
    chat_id = message.chat.id
    phone = message.text
    application = {"name": name, "phone": phone}
    save_application(application)
    msg = bot.send_message(chat_id, "✅ Ваша заявка принята! Мы вам перезвоним.", reply_markup=get_main_menu())
    save_message(chat_id, msg.message_id)

def save_application(application):
    if os.path.exists(APPLICATIONS_FILE):
        with open(APPLICATIONS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
    else:
        data = []
    data.append(application)
    with open(APPLICATIONS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# ---------- СОХРАНЕНИЕ МЕССАДЖЕЙ ----------
def save_message(chat_id, msg_id):
    if chat_id not in user_messages:
        user_messages[chat_id] = []
    user_messages[chat_id].append(msg_id)

# ---------- CALLBACK ----------
@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    if call.data.startswith("tariff_"):
        name = call.data.replace("tariff_", "")
        desc = {
            "Elementary": "Базовый тариф: обучение и настройка рекламы под ключ.",
            "Average": "Средний тариф: маркетинг, аналитика, автоматизация.",
            "PRO": "Премиум тариф: всё включено, персональный менеджер, сайт, реклама."
        }.get(name, "Описание тарифа не найдено.")

        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("🚀 Начать", url=f"https://t.me/{admin_username}"))
        msg = bot.send_message(call.message.chat.id, f"📋 <b>{name}</b>\n\n{desc}", parse_mode="HTML", reply_markup=markup)
        save_message(call.message.chat.id, msg.message_id)

# ---------- FLASK ----------
app = Flask(__name__)
WEBHOOK_URL = "https://botsmm.onrender.com/"  # <-- заменить на свой URL

@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    json_str = request.get_data().decode("utf-8")
    update = telebot.types.Update.de_json(json_str)
    bot.process_new_updates([update])
    return "OK", 200

# ---------- ЗАПУСК ----------
if __name__ == "__main__":
    bot.remove_webhook()
    bot.set_webhook(url=WEBHOOK_URL + TOKEN)
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
