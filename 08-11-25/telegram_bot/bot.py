import threading
from time import sleep
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, CallbackQueryHandler

BOT_TOKEN = "8468258284:AAG2pLTdoPkGRCpFaX2d3g6oX268iKsHGDU"  # 🔒 Replace with your new token

# Background task
def long_running_task(chat_id, message, context: CallbackContext):
    print(f"[Thread] Processing message from chat {chat_id}: {message}")
    sleep(5)  # simulate a long task

    # Send final message
    context.bot.send_message(chat_id=chat_id, text=f"✅ Done processing: {message}")

    # After processing, show switch buttons
    keyboard = [
        [
            InlineKeyboardButton("🟢 Switch ON", callback_data="switch_on"),
            InlineKeyboardButton("🔴 Switch OFF", callback_data="switch_off")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    context.bot.send_message(chat_id=chat_id, text="⚙️ Choose an option:", reply_markup=reply_markup)

# /start command
def start(update: Update, context: CallbackContext):
    update.message.reply_text("👋 Hi! Send me something and I'll process it in a separate thread!")

# /switch command
def switch_control(update: Update, context: CallbackContext):
    keyboard = [
        [
            InlineKeyboardButton("🟢 Switch ON", callback_data="switch_on"),
            InlineKeyboardButton("🔴 Switch OFF", callback_data="switch_off")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text("⚙️ Control Panel:", reply_markup=reply_markup)

# Handles normal user messages
def handle_message(update: Update, context: CallbackContext):
    chat_id = update.message.chat_id
    message = update.message.text

    update.message.reply_text(f"📩 Received: '{message}'\n⏳ Processing in background...")

    # Start a background thread
    t = threading.Thread(target=long_running_task, args=(chat_id, message, context))
    t.start()

# 🆕 Handles button clicks
def button_callback(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()

    if query.data == "switch_on":
        query.edit_message_text("🟢 Switch is ON now!")
        print("[Bot] Switch turned ON")
    elif query.data == "switch_off":
        query.edit_message_text("🔴 Switch is OFF now!")
        print("[Bot] Switch turned OFF")

        

# Main function
def main():
    updater = Updater(BOT_TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("switch", switch_control))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))
    dp.add_handler(CallbackQueryHandler(button_callback))

    print("Bot is listening...")
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
