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

print(f"🔧 Бот запускается с ADMIN_ID = {ADMIN_ID}")

# ==================== КЛАВИАТУРЫ ====================
def get_main_keyboard(is_admin=False):
    buttons = [[KeyboardButton(text="📜 Тест")]]
    if is_admin:
        buttons.append([KeyboardButton(text="👑 Админ панель")])
    print(f"📱 Создана клавиатура. is_admin={is_admin}, кнопок={len(buttons)}")
    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)

def get_admin_keyboard():
    buttons = [
        [KeyboardButton(text="➕ Добавить")],
        [KeyboardButton(text="📋 Список")],
        [KeyboardButton(text="🔙 Назад")]
    ]
    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)

# ==================== ОСНОВНЫЕ КОМАНДЫ ====================
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
    print(f"🖱️ Нажата кнопка 'Тест' от {message.from_user.id}")
    await message.answer("✅ Тест работает!")

@dp.message(F.text == "👑 Админ панель")
async def admin_panel(message: types.Message):
    user_id = message.from_user.id
    print(f"🔥🔥🔥 НАЖАТА АДМИНКА от {user_id}! ADMIN_ID={ADMIN_ID}")
    
    if user_id != ADMIN_ID:
        print(f"❌ ДОСТУП ЗАПРЕЩЁН! {user_id} не равен {ADMIN_ID}")
        await message.answer("❌ Нет прав!")
        return
    
    print(f"✅ ДОСТУП РАЗРЕШЁН! Отправляем админ-клавиатуру...")
    await message.answer("👑 Админ панель", reply_markup=get_admin_keyboard())
    print(f"✅ Клавиатура отправлена")

@dp.message(F.text == "➕ Добавить")
async def add_script(message: types.Message):
    print(f"➕ Добавить скрипт от {message.from_user.id}")
    await message.answer("Функция добавления скриптов скоро будет...")

@dp.message(F.text == "📋 Список")
async def list_scripts(message: types.Message):
    print(f"📋 Список скриптов от {message.from_user.id}")
    await message.answer("Функция списка скриптов скоро будет...")

@dp.message(F.text == "🔙 Назад")
async def back(message: types.Message):
    user_id = message.from_user.id
    is_admin = (user_id == ADMIN_ID)
    print(f"🔙 Назад от {user_id}")
    await message.answer("Главное меню", reply_markup=get_main_keyboard(is_admin))

# ==================== ЗАПУСК ====================
async def main():
    print("🚀 Бот запущен!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
