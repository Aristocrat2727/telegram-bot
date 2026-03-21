#!/usr/bin/env python3
"""
ТЕЛЕГРАМ БОТ СО СПРЯТАННЫМ ТОКЕНОМ
Токен берется из переменной окружения
"""

import telebot
import os
import sys
import json

# === СПРЯТАННЫЙ ТОКЕН ===
# Токен берется из переменной окружения TOKEN
# На Railway: Добавьте переменную TOKEN со значением вашего токена
TOKEN = os.environ.get("TOKEN")
MAIN_ADMIN_ID = 8434489753

# Глобальные переменные
CHATS = []  # Список чатов куда пересылать сообщения
ADMINS = [MAIN_ADMIN_ID]  # Список админов
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

def save_data():
    """Сохраняет данные в файл"""
    data = {
        "chats": CHATS,
        "admins": ADMINS
    }
    with open("bot_data.json", "w") as f:
        json.dump(data, f)

def load_data():
    """Загружает данные из файла"""
    global CHATS, ADMINS
    try:
        with open("bot_data.json", "r") as f:
            data = json.load(f)
            CHATS = data.get("chats", [])
            ADMINS = data.get("admins", [MAIN_ADMIN_ID])
    except:
        # Если файла нет, используем дефолтные значения
        CHATS = []
        ADMINS = [MAIN_ADMIN_ID]

def is_admin(user_id):
    """Проверяет, является ли пользователь админом"""
    return user_id in ADMINS

def is_main_admin(user_id):
    """Проверяет, является ли пользователь главным админом"""
    return user_id == MAIN_ADMIN_ID

# Загружаем сохраненные данные при запуске
load_data()

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
    """Админ отвечает через Reply"""
    replied_message_id = message.reply_to_message.message_id
    
    if replied_message_id in messages:
        user_id = messages[replied_message_id]
        bot.send_message(user_id, message.text)
        
        admin_name = message.from_user.first_name
        if message.from_user.username:
            admin_name += f" (@{message.from_user.username})"
        
        print(f"📨 Ответ от админа {admin_name} → пользователю {user_id}")
        del messages[replied_message_id]

@bot.message_handler(func=lambda m: m.chat.type == "private" and not is_admin(m.from_user.id))
def handle_user_message(message):
    """Сообщение от пользователя - пересылаем во все чаты"""
    try:
        if not CHATS:
            # Если чаты не установлены, сообщаем главному админу
            bot.send_message(MAIN_ADMIN_ID, "⚠️ Нет чатов для пересылки! Используйте /addchat в нужном чате")
            print("⚠️ Нет чатов для пересылки")
            return
        
        user = message.from_user
        user_name = user.first_name + (f" (@{user.username})" if user.username else "")
        
        # Пересылаем во все чаты из списка
        for chat_id in CHATS:
            try:
                # Пересылаем сообщение в чат
                forwarded = bot.forward_message(
                    chat_id=chat_id,
                    from_chat_id=message.chat.id,
                    message_id=message.message_id
                )
                
                # Сохраняем связь между ID пересланного сообщения и ID пользователя
                messages[forwarded.message_id] = message.from_user.id
                
                print(f"📩 Сообщение от {user_name} переслано в чат {chat_id}")
                
            except Exception as e:
                print(f"❌ Ошибка при пересылке в чат {chat_id}: {e}")
        
        # Также отправляем всем админам в личку (кроме главного, если он уже получил)
        for admin_id in ADMINS:
            if admin_id not in CHATS and admin_id != message.from_user.id:
                try:
                    forwarded = bot.forward_message(
                        chat_id=admin_id,
                        from_chat_id=message.chat.id,
                        message_id=message.message_id
                    )
                    messages[forwarded.message_id] = message.from_user.id
                    print(f"📩 Сообщение от {user_name} переслано админу {admin_id}")
                except Exception as e:
                    print(f"❌ Ошибка при пересылке админу {admin_id}: {e}")
        
    except Exception as e:
        print(f"❌ Общая ошибка при пересылке: {e}")

@bot.message_handler(commands=['addchat'])
def handle_addchat(message):
    """Добавление чата для пересылки сообщений"""
    if is_admin(message.from_user.id):
        chat_id = message.chat.id
        
        if chat_id not in CHATS:
            CHATS.append(chat_id)
            save_data()
            
            bot.reply_to(message, f"✅ Чат добавлен для пересылки\nID чата: {chat_id}\nВсего чатов: {len(CHATS)}")
            print(f"💬 Чат добавлен: {chat_id}")
        else:
            bot.reply_to(message, f"⚠️ Этот чат уже в списке\nID: {chat_id}")

@bot.message_handler(commands=['removechat'])
def handle_removechat(message):
    """Удаление чата из списка"""
    if is_admin(message.from_user.id):
        chat_id = message.chat.id
        
        if chat_id in CHATS:
            CHATS.remove(chat_id)
            save_data()
            bot.reply_to(message, f"✅ Чат удален из списка\nID: {chat_id}\nОсталось чатов: {len(CHATS)}")
            print(f"🗑️ Чат удален: {chat_id}")
        else:
            bot.reply_to(message, "❌ Этот чат не в списке")

@bot.message_handler(commands=['listchats'])
def handle_listchats(message):
    """Список всех чатов для пересылки"""
    if is_admin(message.from_user.id):
        if CHATS:
            chats_list = "\n".join([f"💬 {chat_id}" for chat_id in CHATS])
            response = f"📋 Чаты для пересылки ({len(CHATS)}):\n{chats_list}"
        else:
            response = "📭 Нет добавленных чатов"
        bot.reply_to(message, response)

@bot.message_handler(commands=['addadmin'])
def handle_addadmin(message):
    """Добавление нового админа"""
    if is_main_admin(message.from_user.id):
        try:
            command_parts = message.text.split()
            if len(command_parts) == 2:
                new_admin_id = int(command_parts[1])
                
                if new_admin_id not in ADMINS:
                    ADMINS.append(new_admin_id)
                    save_data()
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

@bot.message_handler(commands=['removeadmin'])
def handle_removeadmin(message):
    """Удаление админа"""
    if is_main_admin(message.from_user.id):
        try:
            command_parts = message.text.split()
            if len(command_parts) == 2:
                admin_id = int(command_parts[1])
                
                if admin_id in ADMINS and admin_id != MAIN_ADMIN_ID:
                    ADMINS.remove(admin_id)
                    save_data()
                    bot.reply_to(message, f"✅ Админ {admin_id} удален")
                    print(f"👑 Удален админ: {admin_id}")
                elif admin_id == MAIN_ADMIN_ID:
                    bot.reply_to(message, "❌ Нельзя удалить главного админа")
                else:
                    bot.reply_to(message, "⚠️ Этот пользователь не админ")
            else:
                bot.reply_to(message, "❌ Используйте: /removeadmin USER_ID")
        except ValueError:
            bot.reply_to(message, "❌ Неверный формат ID")

@bot.message_handler(commands=['listadmins'])
def handle_listadmins(message):
    """Список всех админов"""
    if is_admin(message.from_user.id):
        admins_list = []
        for admin_id in ADMINS:
            if admin_id == MAIN_ADMIN_ID:
                admins_list.append(f"👑 {admin_id} (главный)")
            else:
                admins_list.append(f"👤 {admin_id}")
        
        response = f"📋 Админы ({len(ADMINS)}):\n" + "\n".join(admins_list)
        bot.reply_to(message, response)

@bot.message_handler(commands=['status'])
def handle_status(message):
    """Статус бота"""
    if is_admin(message.from_user.id):
        chats_status = f"✅ Чатов: {len(CHATS)}" if CHATS else "❌ Чаты НЕ установлены"
        status_text = f"""🤖 Статус бота:
📊 Сообщений в очереди: {len(messages)}
{chats_status}
👑 Админов: {len(ADMINS)}
🆔 ID этого чата: {message.chat.id}
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
        print(f"🧹 Очередь очищена ({count} сообщений)")

@bot.message_handler(commands=['help', 'commands'])
def handle_help(message):
    """Помощь для админа"""
    if is_admin(message.from_user.id):
        help_text = """📋 КОМАНДЫ ДЛЯ АДМИНА:

🛠 Управление чатами:
/addchat - добавить этот чат для получения сообщений
/removechat - удалить этот чат из списка
/listchats - список всех чатов

👑 Управление админами (только главный):
/addadmin ID - добавить админа
/removeadmin ID - удалить админа
/listadmins - список всех админов

📊 Общие команды:
/status - статус бота
/clear - очистить очередь сообщений
/help - эта справка

📱 КАК НАСТРОИТЬ:
1. Добавьте бота в группу/канал
2. Напишите /addchat в этом чате
3. Повторите для других чатов если нужно
4. Готово!

💬 КАК ОТВЕЧАТЬ:
1. Получите сообщение от пользователя (оно будет переслано)
2. Нажмите Reply на это сообщение
3. Напишите ответ
4. Бот отправит ответ пользователю автоматически"""
        bot.reply_to(message, help_text)

@bot.message_handler(commands=['test'])
def handle_test(message):
    """Тестовая команда для проверки"""
    if is_admin(message.from_user.id):
        if CHATS:
            for chat_id in CHATS:
                try:
                    bot.send_message(chat_id, "✅ Тестовое сообщение от бота")
                except Exception as e:
                    print(f"❌ Ошибка отправки теста в {chat_id}: {e}")
            bot.reply_to(message, f"✅ Тест отправлен в {len(CHATS)} чат(ов)")
        else:
            bot.reply_to(message, "❌ Нет чатов для пересылки")

# Информация при запуске
print("=" * 50)
print("🤖 ТЕЛЕГРАМ БОТ ЗАПУЩЕН")
print("=" * 50)
print(f"👑 Главный админ: {MAIN_ADMIN_ID}")
print(f"👥 Всего админов: {len(ADMINS)}")
print(f"💬 Чатов для пересылки: {len(CHATS)}")
if CHATS:
    print("Список чатов:")
    for chat_id in CHATS:
        print(f"  - {chat_id}")
print("🔒 Токен: СПРЯТАН (из переменной окружения)")
print("=" * 50)

# Запускаем бота
bot.polling(none_stop=True)
