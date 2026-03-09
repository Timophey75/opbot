import os
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from datetime import datetime
import asyncio
import logging
from database import Database

load_dotenv()
API_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '7253076546:AAG_gZ-Ye5yrBVXBFT2T6Pl26D2jQc6p3aY')
ADMIN_CODE = os.getenv('ADMIN_CODE', '0000')
WEBAPP_URL = os.getenv('WEB_APP_URL', 'https://opbot-webapp.onrender.com')

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Инициализация БД
db = Database()

# Инициализация бота
bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# FSM для входа
class LoginStates(StatesGroup):
    waiting_for_code = State()
    logged_in = State()

# Словарь для отслеживания аутентифицированных пользователей
authenticated_users = {}

@dp.message(Command("start"))
async def start_handler(message: types.Message, state: FSMContext):
    """Обработчик команды /start"""
    user_id = message.from_user.id
    
    welcome_text = "👋 Добро пожаловать в систему управления расписанием!\n\n"
    welcome_text += "Нажмите на кнопку ниже чтобы открыть мини-приложение"
    
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[[
            InlineKeyboardButton(
                text="📱 Открыть приложение",
                web_app=WebAppInfo(url=f"{WEBAPP_URL}/app")
            )
        ]]
    )
    
    await message.answer(welcome_text, reply_markup=keyboard)

@dp.message(Command("admin_notify"))
async def admin_notify(message: types.Message):
    """Команда для отправки уведомлений админам (внутри бота)"""
    if message.from_user.id not in [u for u in authenticated_users if authenticated_users[u].get('is_admin')]:
        await message.answer("❌ У вас нет прав на эту команду")
        return
    
    await message.answer("📬 Это место для автоматических уведомлений")

@dp.message(Command("status"))
async def status_handler(message: types.Message):
    """Статус бота"""
    users = db.get_all_users()
    text = f"📊 Статус системы:\n"
    text += f"👥 Пользователей в системе: {len(users)}\n"
    text += f"✅ Бот работает нормально!"
    
    await message.answer(text)

async def send_shift_notification(tg_user_id: int, operator_name: str, date: str, time: str, title: str):
    """Отправляет уведомление оператору о назначении на смену"""
    try:
        message_text = f"📌 <b>Вас назначили на смену!</b>\n\n"
        message_text += f"👤 День: {date}\n"
        message_text += f"⏰ Время: {time}\n"
        message_text += f"📝 Мероприятие: {title}\n"
        message_text += f"\nПроверьте расписание в приложении"
        
        await bot.send_message(tg_user_id, message_text, parse_mode='HTML')
    except Exception as e:
        logger.error(f"Error sending notification: {e}")

async def send_refusal_notification(admin_id: int, operator_name: str, date: str, time: str, reason: str):
    """Отправляет уведомление администратору об отказе от смены"""
    try:
        message_text = f"⚠️ <b>Оператор отказался от смены</b>\n\n"
        message_text += f"👤 Оператор: {operator_name}\n"
        message_text += f"📅 День: {date}\n"
        message_text += f"⏰ Время: {time}\n"
        message_text += f"💬 Причина: {reason}\n"
        message_text += f"\nПроверьте приложение для переназначения"
        
        await bot.send_message(admin_id, message_text, parse_mode='HTML')
    except Exception as e:
        logger.error(f"Error sending refusal notification: {e}")

async def main():
    """Запуск бота"""
    logger.info("Bot starting...")
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())

if __name__ == "__main__":
    asyncio.run(main())
