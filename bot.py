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

print(f"🟢 Бот запущен. ADMIN_ID = {ADMIN_ID}")

def get_main_keyboard(is_admin=False):
    buttons = [[KeyboardButton(text="📜 Тест")]]
    if is_admin:
        buttons.append([KeyboardButton(text="👑 Админка")])
    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)

def get_admin_keyboard():
    buttons = [
        [KeyboardButton(text="➕ Добавить")],
        [KeyboardButton(text="📋 Список")],
        [KeyboardButton(text="🔙 Назад")]
    ]
    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)

@dp.message(Command("start"))
async def start(message: types.Message):
    user_id = message.from_user.id
    is_admin = (user_id == ADMIN_ID)
    print(f"📩 /start от {user_id}. ADMIN_ID={ADMIN_ID}. is_admin={is_admin}")
    await message.answer(
        f"Привет! Твой ID: {user_id}",
        reply_markup=get_main_keyboard(is_admin)
    )

@dp.message(F.text == "📜 Тест")
async def test(message: types.Message):
    print(f"🔘 Тест от {message.from_user.id}")
    await message.answer("✅ Тест")

@dp.message(F.text == "👑 Админка")
async def admin_panel(message: types.Message):
    user_id = message.from_user.id
    print(f"🔥🔥🔥 АДМИНКА от {user_id}")
    if user_id != ADMIN_ID:
        await message.answer("❌ Нет прав")
        return
    await message.answer("Админ панель", reply_markup=get_admin_keyboard())

@dp.message(F.text == "➕ Добавить")
async def add(message: types.Message):
    print(f"➕ Добавить от {message.from_user.id}")
    await message.answer("Добавление скриптов...")

@dp.message(F.text == "📋 Список")
async def lst(message: types.Message):
    print(f"📋 Список от {message.from_user.id}")
    await message.answer("Список скриптов...")

@dp.message(F.text == "🔙 Назад")
async def back(message: types.Message):
    user_id = message.from_user.id
    is_admin = (user_id == ADMIN_ID)
    await message.answer("Главное меню", reply_markup=get_main_keyboard(is_admin))

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
