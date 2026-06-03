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

# Простая клавиатура
def get_main_keyboard(is_admin=False):
    buttons = [[KeyboardButton(text="📜 Тест")]]
    if is_admin:
        buttons.append([KeyboardButton(text="👑 Админка")])
    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)

def get_admin_keyboard():
    buttons = [[KeyboardButton(text="✅ Работает")], [KeyboardButton(text="🔙 Назад")]]
    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)

@dp.message(Command("start"))
async def start(message: types.Message):
    is_admin = (message.from_user.id == ADMIN_ID)
    await message.answer(
        f"Привет, {message.from_user.first_name}!",
        reply_markup=get_main_keyboard(is_admin)
    )

@dp.message(F.text == "📜 Тест")
async def test(message: types.Message):
    await message.answer("✅ Тестовая кнопка работает!")

@dp.message(F.text == "👑 Админка")
async def admin_panel(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        await message.answer("❌ Нет прав!")
        return
    await message.answer("👑 Админ панель", reply_markup=get_admin_keyboard())

@dp.message(F.text == "✅ Работает")
async def admin_test(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return
    await message.answer("✅ Админка работает! Ты можешь добавлять скрипты потом.")

@dp.message(F.text == "🔙 Назад")
async def back(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return
    await message.answer("Главное меню", reply_markup=get_main_keyboard(True))

async def main():
    print("🚀 Тестовый бот запущен!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
