import telebot
import os

TOKEN = '7115848334:AAEOh2QNHpookWgSWeJZpS3gl4RaDVTywkk'
ADMIN_IDS = [5727757258, 6300836232]
TARGET_FILE = 'target_user_ids.txt'
YOUR_FILE = 'your_user_ids.txt'

bot = telebot.TeleBot(TOKEN)

def load_user_ids(filename):
    if not os.path.exists(filename):
        return []
    with open(filename, 'r') as file:
        return [int(line.strip()) for line in file]

def save_user_ids(filename, user_ids):
    with open(filename, 'w') as file:
        for user_id in user_ids:
            file.write(f"{user_id}\n")

def is_admin(user_id):
    return user_id in ADMIN_IDS

def add_user_to_list(user_id, list_type):
    filename = TARGET_FILE if list_type == 'target' else YOUR_FILE
    user_ids = load_user_ids(filename)
    if user_id not in user_ids:
        user_ids.append(user_id)
        save_user_ids(filename, user_ids)
        return True
    return False

def remove_user_from_list(user_id, list_type):
    filename = TARGET_FILE if list_type == 'target' else YOUR_FILE
    user_ids = load_user_ids(filename)
    if user_id in user_ids:
        user_ids.remove(user_id)
        save_user_ids(filename, user_ids)
        return True
    return False

def forward_message_to_you(message):
    try:
        user_id = message.from_user.id if message.from_user else message.sender_chat.id
        first_name = message.from_user.first_name if message.from_user else "Anonymous"
        last_name = message.from_user.last_name if message.from_user else ""
        username = message.from_user.username if message.from_user else "N/A"
        
        chat_title = message.chat.title if message.chat else "N/A"
        chat_username = message.chat.username if message.chat else "N/A"
        chat_link = f"https://t.me/{chat_username}" if chat_username else "N/A"

        for target_user_id in load_user_ids(YOUR_FILE):
            if message.content_type == 'text':
                content = message.text
                bot.send_message(target_user_id, f"Chat Title: {chat_title}\nChat Link: {chat_link}\nID: {user_id}\nName: {first_name} {last_name}\nUsername: @{username}\nMessage: {content}")
            else:
                bot.send_message(target_user_id, f"Chat Title: {chat_title}\nChat Link: {chat_link}\nID: {user_id}\nName: {first_name} {last_name}\nUsername: @{username}\nMessage: Content deleted")
                
                if message.content_type == 'photo':
                    bot.send_photo(target_user_id, message.photo[-1].file_id)
                elif message.content_type == 'video':
                    bot.send_video(target_user_id, message.video.file_id)
                elif message.content_type == 'document':
                    bot.send_document(target_user_id, message.document.file_id)
                elif message.content_type == 'voice':
                    bot.send_voice(target_user_id, message.voice.file_id)
                elif message.content_type == 'audio':
                    bot.send_audio(target_user_id, message.audio.file_id)
                elif message.content_type == 'sticker':
                    bot.send_sticker(target_user_id, message.sticker.file_id)
                elif message.content_type == 'animation':
                    bot.send_animation(target_user_id, message.animation.file_id)
    except Exception as e:
        print(f'Error while forwarding message: {e}')

def delete_message_if_target_user(message):
    # Check if the message is from a channel or group (ID starts with -100 or < 0)
    if message.chat and message.chat.id < 0:
        try:
            bot.delete_message(message.chat.id, message.message_id)
            print(f'Deleted message from channel or group with ID {message.chat.id}')
        except Exception as e:
            print(f'Error: {e}')
        return

    # Check if the message is from a target user in a group or supergroup
    if message.chat and message.chat.type in ['group', 'supergroup']:
        user_ids = load_user_ids(TARGET_FILE)
        if (message.from_user and message.from_user.id in user_ids) or (message.sender_chat and message.sender_chat.id in user_ids):
            forward_message_to_you(message)
            try:
                bot.delete_message(message.chat.id, message.message_id)
                print(f'Deleted message from user {message.from_user.id}' if message.from_user else 'Deleted message from channel or anonymous sender')
            except Exception as e:
                print(f'Error: {e}')

@bot.message_handler(commands=['add_target'])
def handle_add_target(message):
    if is_admin(message.from_user.id):
        try:
            _, user_id = message.text.split()
            user_id = int(user_id)
            if add_user_to_list(user_id, 'target'):
                bot.reply_to(message, f"User ID {user_id} added to TARGET_USER_IDS.")
            else:
                bot.reply_to(message, f"User ID {user_id} already in TARGET_USER_IDS.")
        except Exception as e:
            bot.reply_to(message, f"Error: {e}")

@bot.message_handler(commands=['remove_target'])
def handle_remove_target(message):
    if is_admin(message.from_user.id):
        try:
            _, user_id = message.text.split()
            user_id = int(user_id)
            if remove_user_from_list(user_id, 'target'):
                bot.reply_to(message, f"User ID {user_id} removed from TARGET_USER_IDS.")
            else:
                bot.reply_to(message, f"User ID {user_id} not found in TARGET_USER_IDS.")
        except Exception as e:
            bot.reply_to(message, f"Error: {e}")

@bot.message_handler(commands=['add_your'])
def handle_add_your(message):
    if is_admin(message.from_user.id):
        try:
            _, user_id = message.text.split()
            user_id = int(user_id)
            if add_user_to_list(user_id, 'your'):
                bot.reply_to(message, f"User ID {user_id} added to YOUR_USER_IDS.")
            else:
                bot.reply_to(message, f"User ID {user_id} already in YOUR_USER_IDS.")
        except Exception as e:
            bot.reply_to(message, f"Error: {e}")

@bot.message_handler(commands=['remove_your'])
def handle_remove_your(message):
    if is_admin(message.from_user.id):
        try:
            _, user_id = message.text.split()
            user_id = int(user_id)
            if remove_user_from_list(user_id, 'your'):
                bot.reply_to(message, f"User ID {user_id} removed from YOUR_USER_IDS.")
            else:
                bot.reply_to(message, f"User ID {user_id} not found in YOUR_USER_IDS.")
        except Exception as e:
            bot.reply_to(message, f"Error: {e}")

@bot.message_handler(commands=['cmds'])
def handle_cmds(message):
    if is_admin(message.from_user.id):
        commands_info = (
            "/cmds - عرض قائمة الأوامر\n"
            "/add_target <user_id> - إضافة ID حذف\n"
            "/remove_target <user_id> - حذف ID حذف\n"
            "/add_your <user_id> - إضافة ID استلام رسائل\n"
            "/remove_your <user_id> - حذف ID استلام رسائل\n"
        )
        photo_url = 'https://t.me/mag_pho/97'
        bot.send_video(chat_id=message.chat.id, video=photo_url, caption=commands_info)

@bot.message_handler(content_types=['text', 'photo', 'video', 'document', 'voice', 'audio', 'sticker', 'animation'])
def handle_all_messages(message):
    delete_message_if_target_user(message)

bot.polling()
