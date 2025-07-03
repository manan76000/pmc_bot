
import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from PIL import Image
import io

user_sessions = {}

BEFORE_BOX = (60, 220, 340, 640)
AFTER_BOX = (430, 220, 710, 640)
TEMPLATE_PATH = "template.png"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user_sessions[chat_id] = {"step": "waiting_before"}
    await update.message.reply_text("Welcome! Please send the *Before* photo.")

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    photo_file = await update.message.photo[-1].get_file()
    photo_bytes = await photo_file.download_as_bytearray()
    img = Image.open(io.BytesIO(photo_bytes)).convert("RGB")

    session = user_sessions.get(chat_id, {})

    if session.get("step") == "waiting_before":
        session["before"] = img
        session["step"] = "waiting_after"
        await update.message.reply_text("Got it! Now send the *After* photo.")
    elif session.get("step") == "waiting_after":
        session["after"] = img
        await update.message.reply_text("Generating your before-after image…")
        result = create_before_after_image(session["before"], session["after"])
        output = io.BytesIO()
        output.name = 'before_after.jpg'
        result.save(output, format='JPEG')
        output.seek(0)
        await update.message.reply_photo(photo=output)
        user_sessions[chat_id] = {}  # Reset
    else:
        await update.message.reply_text("Please start with /start")

def create_before_after_image(before, after):
    template = Image.open(TEMPLATE_PATH).convert("RGB")

    before_area = (BEFORE_BOX[2] - BEFORE_BOX[0], BEFORE_BOX[3] - BEFORE_BOX[1])
    after_area = (AFTER_BOX[2] - AFTER_BOX[0], AFTER_BOX[3] - AFTER_BOX[1])

    before = before.resize(before_area)
    after = after.resize(after_area)

    template.paste(before, BEFORE_BOX[:2])
    template.paste(after, AFTER_BOX[:2])

    return template

if __name__ == "__main__":
    TOKEN = "7615101678:AAEnb9h9VBuwJPqcIErGUvvojSkiTzzln_Y"

    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))

    print("Bot running...")
    app.run_polling()
