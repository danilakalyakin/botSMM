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

# ---------- СОХРАНЕНИЕ МЕССАДЖЕЙ ----------
def save_message(chat_id, msg_id):
    if chat_id not in user_messages:
        user_messages[chat_id] = []
    user_messages[chat_id].append(msg_id)

# ---------- ЗАЯВКИ ----------
def save_application(application):
    if os.path.exists(APPLICATIONS_FILE):
        with open(APPLICATIONS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
    else:
        data = []
    data.append(application)
    with open(APPLICATIONS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# ---------- FLASK ----------
app = Flask(__name__)
WEBHOOK_URL = "https://botsmm.onrender.com/"  # твой URL на Render

@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    json_str = request.get_data().decode("utf-8")
    update = telebot.types.Update.de_json(json_str)
    bot.process_new_updates([update])
    return "OK", 200

@app.route("/", methods=["GET"])
def index():
    return "Bot is running!", 200

# ---------- АВТОМАТИЧЕСКАЯ УСТАНОВКА ВЕБХУКА ----------
def set_webhook():
    try:
        info = bot.get_webhook_info()
        if info.url != WEBHOOK_URL + TOKEN:
            bot.remove_webhook()
            bot.set_webhook(url=WEBHOOK_URL + TOKEN)
            print("Webhook установлен ✅")
        else:
            print("Webhook уже установлен")
    except Exception as e:
        print("Ошибка установки вебхука:", e)

# Устанавливаем вебхук через поток при старте
threading.Thread(target=set_webhook).start()

# ---------- ЗАПУСК ----------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
