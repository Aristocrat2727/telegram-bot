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
ADMIN_ID = 5504715265  # Основной админ (можно добавить несколько через запятую)

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

# Хранилище сообщений
messages = {}

# Список админов (можно добавить несколько ID)
admins = [ADMIN_ID]

def is_admin(user_id):
    """Проверяет, является ли пользователь админом"""
    return user_id in admins

@bot.message_handler(commands=['start'])
def handle_start(message):
    """Обработка команды /start"""
    reply_text = "Здравствуйте!\n\nНапишите Ваш вопрос, и мы ответим Вам в ближайшее время."
    bot.reply_to(message, reply_text)
    
    # Лог
    user = message.from_user
    print(f"📝 /start от {user.first_name} (ID: {user.id})")

@bot.message_handler(func=lambda m: m.reply_to_message and is_admin(m.from_user.id))
def handle_admin_reply(message):
    """Админ отвечает через Reply (работает из любого чата)"""
    replied_message_id = message.reply_to_message.message_id
    
    if replied_message_id in messages:
        user_id = messages[replied_message_id]
        
        # Отправляем ответ пользователю
        bot.send_message(user_id, f"📨 Ответ на ваше сообщение:\n\n{message.text}")
        
        # Логирование
        admin_name = message.from_user.first_name
        if message.from_user.username:
            admin_name += f" (@{message.from_user.username})"
        
        print(f"📨 Ответ от админа {admin_name} → пользователю {user_id}")
        
        # Удаляем сообщение из очереди
        del messages[replied_message_id]
        
        # Не отправляем подтверждение в чат (как вы просили)
        # Просто молча отправляем ответ пользователю

@bot.message_handler(func=lambda m: m.chat.type == "private" and not is_admin(m.from_user.id))
def handle_user_message(message):
    """Сообщение от пользователя (только из личных сообщений)"""
    try:
        user = message.from_user
        user_name = user.first_name + (f" (@{user.username})" if user.username else "")
        user_id = user.id
        
        # Создаем информационное сообщение для админа
        admin_message = f"📩 Новое сообщение от пользователя:\n"
        admin_message += f"👤 Имя: {user.first_name}\n"
        if user.username:
            admin_message += f"📱 Ник: @{user.username}\n"
        admin_message += f"🆔 ID: {user_id}\n"
        admin_message += f"📝 Сообщение:\n\n{message.text}"
        
        # Отправляем сообщение всем админам
        for admin_id in admins:
            try:
                # Отправляем информационное сообщение
                sent_msg = bot.send_message(admin_id, admin_message)
                # Сохраняем ID отправленного сообщения
                messages[sent_msg.message_id] = user_id
                print(f"📨 Сообщение от {user_name} отправлено админу {admin_id}")
            except Exception as e:
                print(f"❌ Не удалось отправить сообщение админу {admin_id}: {e}")
        
    except Exception as e:
        print(f"❌ Ошибка обработки сообщения: {e}")

@bot.message_handler(commands=['status'])
def handle_status(message):
    """Статус бота"""
    if is_admin(message.from_user.id):
        status_text = f"""🤖 Статус бота:
📊 Сообщений в очереди: {len(messages)}
👑 Админов: {len(admins)}
✅ Бот работает нормально"""
        bot.reply_to(message, status_text)
        print(f"📊 Админ {message.from_user.id} запросил статус")

@bot.message_handler(commands=['clear'])
def handle_clear(message):
    """Очистка очереди"""
    if is_admin(message.from_user.id):
        count = len(messages)
        messages.clear()
        bot.reply_to(message, f"✅ Очередь очищена ({count} сообщений удалено)")
        print(f"🧹 Админ {message.from_user.id} очистил очередь ({count} сообщений)")

@bot.message_handler(commands=['addadmin'])
def handle_addadmin(message):
    """Добавление нового админа (только для основного админа)"""
    if message.from_user.id == ADMIN_ID:
        try:
            # Пытаемся получить ID из команды /addadmin 123456789
            command_parts = message.text.split()
            if len(command_parts) == 2:
                new_admin_id = int(command_parts[1])
                
                if new_admin_id not in admins:
                    admins.append(new_admin_id)
                    bot.reply_to(message, f"✅ Пользователь {new_admin_id} добавлен в админы")
                    print(f"👑 Добавлен новый админ: {new_admin_id}")
                else:
                    bot.reply_to(message, "⚠️ Этот пользователь уже админ")
            else:
                bot.reply_to(message, "❌ Используйте: /addadmin USER_ID")
        except ValueError:
            bot.reply_to(message, "❌ Неверный формат ID")
        except Exception as e:
            bot.reply_to(message, f"❌ Ошибка: {e}")

@bot.message_handler(commands=['listadmins'])
def handle_listadmins(message):
    """Список админов"""
    if is_admin(message.from_user.id):
        admins_list = "\n".join([f"👑 {admin_id}" for admin_id in admins])
        bot.reply_to(message, f"📋 Список админов:\n{admins_list}")

# Информация при запуске
print("=" * 50)
print("🤖 ТЕЛЕГРАМ БОТ ЗАПУЩЕН")
print("=" * 50)
print(f"👑 Админы: {admins}")
print("📱 Бот отвечает только на личные сообщения от пользователей")
print("🔐 Админы могут отвечать из любого чата через Reply")
print("🔒 Токен: СПРЯТАН (из переменной окружения)")
print("=" * 50)

# Запускаем бота
bot.polling(none_stop=True)
