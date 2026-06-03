import os
import asyncio
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

def get_main_keyboard(is_admin=False):
    buttons = [[KeyboardButton(text="📜 Все скрипты")], [KeyboardButton(text="🔎 Поиск")], [KeyboardButton(text="📖 Помощь")]]
    if is_admin:
        buttons.append([KeyboardButton(text="👑 Админ панель")])
    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)

def get_admin_keyboard():
    return ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="➕ Добавить")], [KeyboardButton(text="📋 Список")], [KeyboardButton(text="🔙 Назад")]], resize_keyboard=True)

@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer("Главное меню", reply_markup=get_main_keyboard(message.from_user.id == ADMIN_ID))

@dp.message(F.text == "👑 Админ панель")
async def admin(message: types.Message):
    if message.from_user.id == ADMIN_ID:
        await message.answer("Админ панель", reply_markup=get_admin_keyboard())
    else:
        await message.answer("Нет прав")

@dp.message(F.text == "🔙 Назад")
async def back(message: types.Message):
    await message.answer("Главное меню", reply_markup=get_main_keyboard(message.from_user.id == ADMIN_ID))

@dp.message(F.text == "➕ Добавить")
async def add(message: types.Message):
    await message.answer("Добавление скриптов")

@dp.message(F.text == "📋 Список")
async def lst(message: types.Message):
    await message.answer("Список скриптов")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
