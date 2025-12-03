#!/usr/bin/env python3
"""
ТЕЛЕГРАМ БОТ СО СПРЯТАННЫМ ТОКЕНОМ
Токен берется из переменной окружения
"""

import telebot
import os
import sys

# === СПРЯТАННЫЙ ТОКЕН ===
# Токен берется из переменной окружения TOKEN
# На Railway: Добавьте переменную TOKEN со значением вашего токена
TOKEN = os.environ.get("TOKEN")
ADMIN_ID = 5504715265
CHAT_ID = None  # ID чата куда пересылать сообщения

# Проверяем что токен есть
if not TOKEN:
    print("❌ ОШИБКА: Токен не найден!")
    print("📝 Добавьте переменную окружения TOKEN:")
    print("   На Railway: Variables → New Variable")
    print("   На Termux: export TOKEN='ваш_токен'")
    print("   На Replit: Secrets → New Secret")
    sys.exit(1)

# Создаем бота
bot = telebot.TeleBot(TOKEN)

# Хранилище сообщений (связываем ID пересланного сообщения с ID пользователя)
messages = {}

@bot.message_handler(commands=['start'])
def handle_start(message):
    """Обработка команды /start"""
    reply_text = "Здравствуйте!\n\nНапишите Ваш вопрос, и мы ответим Вам в ближайшее время."
    bot.reply_to(message, reply_text)
    
    # Лог
    user = message.from_user
    print(f"📝 /start от {user.first_name} (ID: {user.id})")

@bot.message_handler(func=lambda m: m.reply_to_message and m.from_user.id == ADMIN_ID)
def handle_admin_reply(message):
    """Админ отвечает через Reply"""
    replied_message_id = message.reply_to_message.message_id
    
    if replied_message_id in messages:
        user_id = messages[replied_message_id]
        bot.send_message(user_id, message.text)
        print(f"📨 Ответ → {user_id}")
        del messages[replied_message_id]

@bot.message_handler(func=lambda m: m.chat.type == "private" and m.from_user.id != ADMIN_ID)
def handle_user_message(message):
    """Сообщение от пользователя - пересылаем в чат"""
    try:
        # Проверяем, указан ли CHAT_ID
        if CHAT_ID is None:
            print("⚠️ CHAT_ID не указан. Сообщение не будет переслано.")
            return
            
        # Пересылаем сообщение в чат
        forwarded = bot.forward_message(
            chat_id=CHAT_ID,
            from_chat_id=message.chat.id,
            message_id=message.message_id
        )
        
        # Сохраняем связь между ID пересланного сообщения и ID пользователя
        messages[forwarded.message_id] = message.from_user.id
        
        user = message.from_user
        user_name = user.first_name + (f" (@{user.username})" if user.username else "")
        print(f"📩 Сообщение от {user_name} переслано в чат {CHAT_ID}")
        
    except Exception as e:
        print(f"❌ Ошибка при пересылке: {e}")

@bot.message_handler(commands=['setchat'])
def handle_setchat(message):
    """Установка чата для пересылки сообщений"""
    if message.from_user.id == ADMIN_ID:
        global CHAT_ID
        CHAT_ID = message.chat.id
        bot.reply_to(message, f"✅ Чат для пересылки установлен (ID: {CHAT_ID})")
        print(f"💬 Чат для пересылки установлен: {CHAT_ID}")

@bot.message_handler(commands=['status'])
def handle_status(message):
    """Статус бота"""
    if message.from_user.id == ADMIN_ID:
        chat_status = f"Чат установлен: {CHAT_ID}" if CHAT_ID else "Чат НЕ установлен (используйте /setchat)"
        status_text = f"""🤖 Статус бота:
📊 Сообщений в очереди: {len(messages)}
💬 {chat_status}
✅ Бот работает нормально"""
        bot.reply_to(message, status_text)
        print(f"📊 Админ запросил статус")

@bot.message_handler(commands=['clear'])
def handle_clear(message):
    """Очистка очереди"""
    if message.from_user.id == ADMIN_ID:
        messages.clear()
        bot.reply_to(message, "✅ Очередь очищена")
        print("🧹 Очередь очищена")

@bot.message_handler(commands=['help'])
def handle_help(message):
    """Помощь для админа"""
    if message.from_user.id == ADMIN_ID:
        help_text = """📋 Команды для админа:
/setchat - установить этот чат для получения сообщений
/status - статус бота
/clear - очистить очередь сообщений
/help - эта справка

Как использовать:
1. Напишите /setchat в чате, куда должны приходить сообщения от пользователей
2. Пользователи пишут боту в ЛС
3. Их сообщения пересылаются в этот чат
4. Чтобы ответить - используйте Reply на пересланное сообщение"""
        bot.reply_to(message, help_text)

# Информация при запуске
print("=" * 50)
print("🤖 ТЕЛЕГРАМ БОТ ЗАПУЩЕН")
print("=" * 50)
print(f"👑 Админ ID: {ADMIN_ID}")
print(f"💬 ID чата для пересылки: {'НЕ УСТАНОВЛЕН' if CHAT_ID is None else CHAT_ID}")
print("📝 Для настройки админ должен написать /setchat в нужном чате")
print("🔒 Токен: СПРЯТАН (из переменной окружения)")
print("=" * 50)

# Запускаем бота
bot.polling(none_stop=True)
