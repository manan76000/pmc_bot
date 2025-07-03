
import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from PIL import Image

TOKEN = os.environ.get("TOKEN")
IMAGE_DIR = "images"

# Ensure image directory exists
os.makedirs(IMAGE_DIR, exist_ok=True)

user_images = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Send me two images:
1. Before
2. After")

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    photo_file = await update.message.photo[-1].get_file()
    image_path = os.path.join(IMAGE_DIR, f"{user_id}_{len(user_images.get(user_id, []))}.jpg")
    await photo_file.download_to_drive(image_path)

    user_images.setdefault(user_id, []).append(image_path)

    if len(user_images[user_id]) == 2:
        combined = create_template_image(user_images[user_id][0], user_images[user_id][1])
        combined_path = os.path.join(IMAGE_DIR, f"{user_id}_combined.jpg")
        combined.save(combined_path)
        await update.message.reply_photo(photo=open(combined_path, "rb"))
        user_images[user_id] = []
    else:
        await update.message.reply_text("Now send the second image.")

def create_template_image(before_path, after_path):
    template = Image.open("template.png").convert("RGBA")
    before = Image.open(before_path).resize((450, 450))
    after = Image.open(after_path).resize((450, 450))
    template.paste(before, (100, 270))
    template.paste(after, (680, 270))
    return template

if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    app.run_polling()
