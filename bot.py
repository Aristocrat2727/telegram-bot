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

# Глобальные переменные
CHAT_ID = None  # ID чата куда пересылать сообщения
messages = {}   # Хранилище сообщений {message_id: user_id}

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

def save_chat_id(chat_id):
    """Сохраняет CHAT_ID в файл"""
    with open("chat_id.txt", "w") as f:
        f.write(str(chat_id))

def load_chat_id():
    """Загружает CHAT_ID из файла"""
    try:
        with open("chat_id.txt", "r") as f:
            return int(f.read().strip())
    except:
        return None

# Загружаем сохраненный CHAT_ID при запуске
CHAT_ID = load_chat_id()

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
        print(f"📨 Ответ от админа {message.from_user.id} → пользователю {user_id}")
        del messages[replied_message_id]

@bot.message_handler(func=lambda m: m.chat.type == "private" and m.from_user.id != ADMIN_ID)
def handle_user_message(message):
    """Сообщение от пользователя - пересылаем в чат"""
    try:
        if CHAT_ID is None:
            # Если чат не установлен, сообщаем админу
            bot.send_message(ADMIN_ID, "⚠️ CHAT_ID не установлен! Используйте /setchat в нужном чате")
            print("⚠️ CHAT_ID не установлен")
            return
            
        # Пересылаем сообщение в чат (ФОРВАРД, не отправляем текст!)
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
        bot.send_message(ADMIN_ID, f"❌ Ошибка при пересылке: {e}")

@bot.message_handler(commands=['setchat'])
def handle_setchat(message):
    """Установка чата для пересылки сообщений"""
    if message.from_user.id == ADMIN_ID:
        global CHAT_ID
        CHAT_ID = message.chat.id
        save_chat_id(CHAT_ID)  # Сохраняем в файл
        
        bot.reply_to(message, f"✅ Чат для пересылки установлен\nID чата: {CHAT_ID}")
        print(f"💬 Чат для пересылки установлен: {CHAT_ID}")
        
        # Отправляем тестовое сообщение
        bot.send_message(CHAT_ID, "✅ Бот настроен! Теперь сообщения от пользователей будут приходить сюда.")

@bot.message_handler(commands=['status'])
def handle_status(message):
    """Статус бота"""
    if message.from_user.id == ADMIN_ID:
        chat_status = f"✅ Чат установлен: {CHAT_ID}" if CHAT_ID else "❌ Чат НЕ установлен"
        status_text = f"""🤖 Статус бота:
📊 Сообщений в очереди: {len(messages)}
{chat_status}
🆔 ID этого чата: {message.chat.id}
✅ Бот работает нормально"""
        bot.reply_to(message, status_text)
        print(f"📊 Админ запросил статус")

@bot.message_handler(commands=['clear'])
def handle_clear(message):
    """Очистка очереди"""
    if message.from_user.id == ADMIN_ID:
        count = len(messages)
        messages.clear()
        bot.reply_to(message, f"✅ Очередь очищена ({count} сообщений удалено)")
        print(f"🧹 Очередь очищена ({count} сообщений)")

@bot.message_handler(commands=['help', 'commands'])
def handle_help(message):
    """Помощь для админа"""
    if message.from_user.id == ADMIN_ID:
        help_text = """📋 КОМАНДЫ ДЛЯ АДМИНА:

/setchat - установить этот чат для получения сообщений
/status - показать статус бота
/clear - очистить очередь сообщений
/help - показать эту справку

📱 КАК НАСТРОИТЬ:
1. Добавьте бота в группу/канал
2. Напишите /setchat в этом чате
3. Готово! Теперь сообщения от пользователей будут пересылаться сюда

💬 КАК ОТВЕЧАТЬ:
1. Получите сообщение от пользователя (оно будет переслано)
2. Нажмите Reply на это сообщение
3. Напишите ответ
4. Бот отправит ответ пользователю автоматически"""
        bot.reply_to(message, help_text)

@bot.message_handler(commands=['test'])
def handle_test(message):
    """Тестовая команда для проверки"""
    if message.from_user.id == ADMIN_ID:
        if CHAT_ID:
            bot.send_message(CHAT_ID, "✅ Тестовое сообщение от бота")
            bot.reply_to(message, f"✅ Тест отправлен в чат {CHAT_ID}")
        else:
            bot.reply_to(message, "❌ CHAT_ID не установлен. Сначала используйте /setchat")

# Информация при запуске
print("=" * 50)
print("🤖 ТЕЛЕГРАМ БОТ ЗАПУЩЕН")
print("=" * 50)
print(f"👑 Админ ID: {ADMIN_ID}")
if CHAT_ID:
    print(f"💬 Чат для пересылки: {CHAT_ID} (загружен из файла)")
else:
    print("💬 Чат для пересылки: НЕ УСТАНОВЛЕН")
print("🔒 Токен: СПРЯТАН (из переменной окружения)")
print("=" * 50)

# Запускаем бота
bot.polling(none_stop=True)
