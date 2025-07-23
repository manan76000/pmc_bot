
import telebot

TOKEN = "7615101678:AAEnb9h9VBuwJPqcIErGUvvojSkiTzzln_Y"  # ⚠️ Replace with new token if reset
bot = telebot.TeleBot(TOKEN)

# Remove webhook to avoid conflict error
bot.remove_webhook()

# Define handlers (example)
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Hello! I'm your PMC Bot.")

# Start polling
bot.polling(none_stop=True)


