import logging
from aiogram import Bot, Dispatcher, types, executor
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from dotenv import load_dotenv
import os
import mysql.connector
from datetime import datetime
import asyncio

# Load environment variables
load_dotenv()

# Bot configuration
API_TOKEN = os.getenv('API_TOKEN')
ADMIN_IDS = [int(id) for id in os.getenv('ADMIN_IDS').split(',')]

# Database configuration
db_config = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD', ''),
    'database': os.getenv('DB_NAME', 'joblance')
}

# Logging configuration
logging.basicConfig(level=logging.INFO)

# Bot initialization
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

# Database connection function
def get_db_connection():
    return mysql.connector.connect(**db_config)

# Yangi ish qo'shilganda barcha foydalanuvchilarga xabar yuborish
async def notify_all_users_about_new_job(job_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        # Yangi qo'shilgan ishni olish
        cursor.execute("""
            SELECT j.*, u.name as employer_name 
            FROM jobs j 
            JOIN users u ON j.user_id = u.id 
            WHERE j.id = %s
        """, (job_id,))
        job = cursor.fetchone()
        
        if not job:
            return
            
        # Barcha foydalanuvchilarni olish
        cursor.execute("SELECT telegram_id FROM users")
        users = cursor.fetchall()
        
        # Ish haqida xabar tayyorlash
        job_text = f"""
🎉 Yangi ish qo'shildi!

🏢 {job['title']}
👤 Ish beruvchi: {job['employer_name']}
📍 Hudud: {job['region']}
💼 Ish turi: {job['job_type']}
💰 Maosh: {job['salary_type']}
📝 {job['description'][:200]}...
        """
        
        # Foydalanuvchilarni guruhlarga bo'lish
        user_groups = [users[i:i + 100] for i in range(0, len(users), 100)]
        
        # Har bir guruhga xabar yuborish
        for group in user_groups:
            for user in group:
                try:
                    keyboard = InlineKeyboardMarkup()
                    keyboard.add(InlineKeyboardButton("Ilovaga kirish", url="https://t.me/Joblanceuzbot/joblanceuz"))
                    
                    await bot.send_message(
                        chat_id=user['telegram_id'],
                        text=job_text,
                        reply_markup=keyboard
                    )
                except Exception as e:
                    print(f"Xabar yuborishda xatolik: {e}")
                
    except mysql.connector.Error as err:
        print(f"Database error: {err}")
    finally:
        cursor.close()
        conn.close()

# Message handlers
@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton("Ilovaga kirish", url="https://t.me/Joblanceuzbot/joblanceuz"))
    
    welcome_text = f"""
Salom, {message.from_user.first_name}! 👋

Joblance ilovasidan foydalnish uchun ushbu tugmani bosing
    """
    await message.answer(welcome_text, reply_markup=keyboard)

# Doimiy ravishda bazani tekshirib turish
async def check_new_jobs():
    last_job_id = 0
    while True:
        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            
            # Oxirgi qo'shilgan ishni olish
            cursor.execute("""
                SELECT id FROM jobs 
                ORDER BY created_at DESC 
                LIMIT 1
            """)
            latest_job = cursor.fetchone()
            
            if latest_job and latest_job['id'] > last_job_id:
                # Yangi ish qo'shilgan
                await notify_all_users_about_new_job(latest_job['id'])
                last_job_id = latest_job['id']
            
            cursor.close()
            conn.close()
            
        except Exception as e:
            print(f"Error checking new jobs: {e}")
        
        # 24 soat kutish
        await asyncio.sleep(86400)  # 24 soat = 86400 soniya

if __name__ == '__main__':
    # Doimiy ravishda bazani tekshirib turish
    loop = asyncio.get_event_loop()
    loop.create_task(check_new_jobs())
    
    # Botni ishga tushirish
    executor.start_polling(dp, skip_updates=True)