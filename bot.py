import telebot
from telebot import types
from flask import Flask, request
import json
import os
import time

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
def get_main_menu(chat_id=None):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("📚 Кейсы", "👨‍🏫 Тарифы")
    markup.add("📞 Поддержка", "🧹 Очистить чат")
    markup.add("ℹ️ О боте", "📝 Оставить заявку")
    
    # Если это админ, добавляем кнопку "📢 Рассылка"
    if chat_id == ADMIN_CHAT_ID:
        markup.add("📢 Рассылка")
    return markup

# ---------- СОХРАНЕНИЕ МЕССАДЖЕЙ ----------
def save_message(chat_id, msg_id):
    if chat_id not in user_messages:
        user_messages[chat_id] = []
    user_messages[chat_id].append(msg_id)

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
    chat_id = message.chat.id
    text = message.text
    save_message(chat_id, message.message_id)  # сохраняем сообщение пользователя

    if text == "📚 Кейсы":
        send_cases(message)
    elif text == "👨‍🏫 Тарифы":
        send_tariffs(message)
    elif text == "📞 Поддержка":
        send_support_link(message)
    elif text == "🧹 Очистить чат":
        clear_chat(message)
    elif text == "ℹ️ О боте":
        show_about(message)
    elif text == "📝 Оставить заявку":
        start_application(message)
    elif text == "📢 Рассылка" and chat_id == ADMIN_CHAT_ID:
        msg = bot.send_message(ADMIN_CHAT_ID, "📝 Введите текст для рассылки всем пользователям:")
        bot.register_next_step_handler(msg, broadcast_send)
    else:
        msg = bot.send_message(chat_id, "Я не понимаю эту команду 😅", reply_markup=get_main_menu(chat_id))
        save_message(chat_id, msg.message_id)


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
        time.sleep(0.1)  # чтобы Telegram не блокировал быстрые отправки

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
        time.sleep(0.1)

# ---------- ПОДДЕРЖКА ----------
def send_support_link(message):
    link = f"https://t.me/{admin_username}"
    msg = bot.send_message(message.chat.id, f"📞 Связаться с администратором можно здесь: {link}", reply_markup=get_main_menu())
    save_message(message.chat.id, msg.message_id)

# ---------- ОЧИСТКА ЧАТА ----------
def clear_chat(message):
    chat_id = message.chat.id
    msgs = user_messages.get(chat_id, [])

    if not msgs:
        msg = bot.send_message(chat_id, "⚠️ В чате нет сообщений для удаления.", reply_markup=get_main_menu())
        save_message(chat_id, msg.message_id)
        return

    try:
        anim_msg = bot.send_message(chat_id, "🧹 Очистка чата: 0%")
        save_message(chat_id, anim_msg.message_id)
    except:
        anim_msg = None

    total = len(msgs)
    for i, msg_id in enumerate(msgs):
        try:
            bot.delete_message(chat_id, msg_id)
        except:
            pass

        if anim_msg and i % 5 == 0:
            try:
                percent = int((i / total) * 100)
                bot.edit_message_text(f"🧹 Очистка чата: {percent}%", chat_id, anim_msg.message_id)
            except:
                pass
        time.sleep(0.05)

    # Финальное сообщение
    if anim_msg:
        try:
            bot.edit_message_text("✅ Ваш чат очищен!", chat_id, anim_msg.message_id, reply_markup=get_main_menu())
        except:
            bot.send_message(chat_id, "✅ Ваш чат очищен!", reply_markup=get_main_menu())
    else:
        bot.send_message(chat_id, "✅ Ваш чат очищен!", reply_markup=get_main_menu())

    user_messages[chat_id] = []

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

    # Сохраняем в файл
    save_application(application)

    # 🔹 Отправляем администратору в Telegram
    admin_chat_id = 865082717  # <-- замените на свой Telegram ID
    bot.send_message(admin_chat_id, f"📩 Новая заявка:\nИмя: {name}\nТелефон: {phone}")

    # Сообщение пользователю
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

# ---------- РАССЫЛКА ДЛЯ АДМИНА ----------
ADMIN_CHAT_ID = 865082717  # Telegram ID администратора

@bot.message_handler(commands=['broadcast'])
def broadcast_start(message):
    if message.chat.id != ADMIN_CHAT_ID:
        return  # Только админ может использовать
    msg = bot.send_message(ADMIN_CHAT_ID, "📝 Введите текст для рассылки всем пользователям:")
    bot.register_next_step_handler(msg, broadcast_send)

def broadcast_send(message):
    if message.chat.id != ADMIN_CHAT_ID:
        return
    text_to_send = message.text
    count = 0
    failed = 0
    for chat_id in user_messages.keys():
        try:
            bot.send_message(chat_id, text_to_send)
            count += 1
        except:
            failed += 1
    bot.send_message(ADMIN_CHAT_ID, f"✅ Рассылка завершена!\nОтправлено: {count}\nНе удалось отправить: {failed}")


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
