import logging
from aiogram import Bot, Dispatcher, types, executor
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from dotenv import load_dotenv
import os
from config import API_TOKEN, ADMIN_IDS

# Load environment variables
load_dotenv()

# Bot configuration
API_TOKEN = os.getenv('API_TOKEN')
ADMIN_IDS = [int(id) for id in os.getenv('ADMIN_IDS').split(',')]

# Logging configuration
logging.basicConfig(level=logging.INFO)

# Bot initialization
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)


@dp.message_handler()
async def send_welcome(message: types.Message):
   
   keyboard = InlineKeyboardMarkup()
   keyboard.add(InlineKeyboardButton("🔥 Boshlash", url="https://t.me/Joblanceuzbot/joblanceuz"))

   welcome_text = f"""
Salom, {message.from_user.first_name}! 👋

Joblance ilovasidan foydalnish uchun ushbu tugmani bosing
"""
   await message.answer(welcome_text, reply_markup=keyboard)

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)