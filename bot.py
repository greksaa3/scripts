import os
import asyncio
from datetime import datetime
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from database import db

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))
LOG_CHANNEL_ID = os.getenv("LOG_CHANNEL_ID")
if LOG_CHANNEL_ID:
    LOG_CHANNEL_ID = int(LOG_CHANNEL_ID)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

search_results = {}
search_mode = {}

# ==================== КЛАВИАТУРЫ ====================
def get_main_keyboard(is_admin=False):
    keyboard = [
        [KeyboardButton(text="📜 Все скрипты")],
        [KeyboardButton(text="🔎 Поиск")],
        [KeyboardButton(text="📖 Помощь")]
    ]
    if is_admin:
        keyboard.append([KeyboardButton(text="👑 Админ панель")])
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)

def get_admin_keyboard():
    keyboard = [
        [KeyboardButton(text="➕ Добавить скрипт")],
        [KeyboardButton(text="📋 Список скриптов")],
        [KeyboardButton(text="📢 Рассылка")],
        [KeyboardButton(text="🔙 Назад")]
    ]
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)

def get_paginated_keyboard(items, page, per_page=5):
    if not items:
        return InlineKeyboardMarkup(inline_keyboard=[]), 1
    total = (len(items) + per_page - 1) // per_page
    start = (page - 1) * per_page
    end = start + per_page
    current = items[start:end]
    
    keyboard = []
    for item in current:
        sid, name = item[0], item[1]
        short = name[:35] + "..." if len(name) > 35 else name
        keyboard.append([InlineKeyboardButton(text=f"📜 {short}", callback_data=f"script_{sid}")])
    
    nav = []
    if page > 1:
        nav.append(InlineKeyboardButton(text="⬅️ Назад", callback_data=f"page_{page-1}"))
    if page < total:
        nav.append(InlineKeyboardButton(text="➡️ Вперед", callback_data=f"page_{page+1}"))
    if nav:
        keyboard.append(nav)
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard), total

# ==================== ОСНОВНЫЕ КОМАНДЫ ====================
@dp.message(Command("start"))
async def start(message: types.Message):
    db.add_user(message.from_user.id, message.from_user.username, message.from_user.first_name)
    is_admin = (message.from_user.id == ADMIN_ID)
    await message.answer(
        f"🎮 *ROBLOX SCRIPT HUB*\n\nПривет, {message.from_user.first_name}!\n\nИспользуй кнопки ниже:",
        parse_mode="Markdown",
        reply_markup=get_main_keyboard(is_admin)
    )

@dp.message(F.text == "📜 Все скрипты")
async def all_scripts(message: types.Message):
    scripts = db.get_all_scripts()
    if not scripts:
        await message.answer("📭 Пока нет скриптов!")
        return
    search_results[message.from_user.id] = scripts
    keyboard, total = get_paginated_keyboard(scripts, 1)
    await message.answer(f"📚 *Скрипты* - {len(scripts)} шт.\n📄 Страница 1 из {total}", parse_mode="Markdown", reply_markup=keyboard)

@dp.message(F.text == "🔎 Поиск")
async def search_start(message: types.Message):
    search_mode[message.from_user.id] = True
    await message.answer("🔍 *Введи название скрипта:*", parse_mode="Markdown")

@dp.message(F.text == "📖 Помощь")
async def help_command(message: types.Message):
    await message.answer(
        "📚 *Помощь*\n\n"
        "📜 Все скрипты - показать все скрипты\n"
        "🔎 Поиск - найти по названию\n\n"
        "*Как использовать:*\n"
        "1. Скачай executor\n"
        "2. Скопируй скрипт\n"
        "3. Вставь и Execute",
        parse_mode="Markdown"
    )

# ==================== ПОИСК ====================
@dp.message(F.text)
async def handle_search(message: types.Message):
    user_id = message.from_user.id
    
    if search_mode.get(user_id):
        del search_mode[user_id]
        results = db.search_scripts(message.text)
        if not results:
            await message.answer(f"❌ Ничего не найдено по '{message.text}'")
            return
        search_results[user_id] = results
        keyboard, total = get_paginated_keyboard(results, 1)
        await message.answer(f"🔍 *Результаты:* {len(results)} скриптов\n📄 Страница 1 из {total}", parse_mode="Markdown", reply_markup=keyboard)

# ==================== АДМИН ПАНЕЛЬ ====================
admin_states = {}

@dp.message(F.text == "👑 Админ панель")
async def admin_panel(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        await message.answer("❌ Нет прав!")
        return
    await message.answer("👑 Админ панель", reply_markup=get_admin_keyboard())

@dp.message(F.text == "🔙 Назад")
async def back_to_main(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        await message.answer("❌ Нет прав!")
        return
    await message.answer("Главное меню:", reply_markup=get_main_keyboard(True))

@dp.message(F.text == "➕ Добавить скрипт")
async def add_script_start(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return
    admin_states[message.from_user.id] = {"step": "name"}
    await message.answer("📝 *Введи название скрипта:*", parse_mode="Markdown")

@dp.message(F.text == "📋 Список скриптов")
async def list_scripts(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return
    scripts = db.get_all_scripts()
    if not scripts:
        await message.answer("📭 Нет скриптов")
        return
    buttons = [[InlineKeyboardButton(text=f"❌ {s[1][:30]}", callback_data=f"del_{s[0]}")] for s in scripts]
    await message.answer("📋 *Список скриптов* (нажми для удаления):", parse_mode="Markdown",
                         reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons))

@dp.message(F.text == "📢 Рассылка")
async def broadcast_start(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return
    admin_states[message.from_user.id] = {"step": "broadcast"}
    await message.answer("📢 Отправь сообщение для рассылки:")

@dp.message(F.text)
async def admin_input(message: types.Message):
    user_id = message.from_user.id
    if user_id != ADMIN_ID or user_id not in admin_states:
        return
    
    state = admin_states[user_id]
    step = state.get("step")
    
    if step == "name":
        state["name"] = message.text.strip()
        state["step"] = "code"
        await message.answer("💻 *Отправь LUA код:*", parse_mode="Markdown")
    elif step == "code":
        db.add_script(state["name"], message.text)
        await message.answer(f"✅ Скрипт *{state['name']}* добавлен!", parse_mode="Markdown")
        del admin_states[user_id]
    elif step == "broadcast":
        users = db.get_all_users()
        if not users:
            await message.answer("❌ Нет пользователей!")
            del admin_states[user_id]
            return
        status = await message.answer(f"📡 Рассылка для {len(users)} пользователей...")
        success, fail = 0, 0
        for i, user in enumerate(users):
            try:
                await message.copy_to(user[0])
                success += 1
            except:
                fail += 1
            if i % 10 == 0:
                await asyncio.sleep(0.5)
        await status.edit_text(f"✅ Рассылка завершена!\n✅ Успешно: {success}\n❌ Ошибок: {fail}")
        del admin_states[user_id]

# ==================== КОЛБЭКИ ====================
@dp.callback_query(lambda c: c.data and c.data.startswith("script_"))
async def view_script(callback: types.CallbackQuery):
    script_id = int(callback.data.replace("script_", ""))
    script = db.get_script_by_id(script_id)
    if not script:
        await callback.answer("Скрипт не найден!", show_alert=True)
        return
    _, name, code = script
    await callback.message.answer(f"📜 *{name}*\n\n```lua\n{code}\n```", parse_mode="Markdown")
    await callback.answer()

@dp.callback_query(lambda c: c.data and c.data.startswith("page_"))
async def paginate(callback: types.CallbackQuery):
    page = int(callback.data.replace("page_", ""))
    scripts = search_results.get(callback.from_user.id, db.get_all_scripts())
    if not scripts:
        await callback.answer("Устарело", show_alert=True)
        return
    keyboard, total = get_paginated_keyboard(scripts, page)
    await callback.message.edit_text(f"📚 *Скрипты*\n📄 Страница {page} из {total}", parse_mode="Markdown", reply_markup=keyboard)
    await callback.answer()

@dp.callback_query(lambda c: c.data and c.data.startswith("del_"))
async def delete_script(callback: types.CallbackQuery):
    if callback.from_user.id != ADMIN_ID:
        await callback.answer("❌ Нет прав!", show_alert=True)
        return
    script_id = int(callback.data.replace("del_", ""))
    db.delete_script(script_id)
    await callback.message.edit_text("✅ Скрипт удалён!")
    await callback.answer()

# ==================== ЗАПУСК ====================
async def main():
    print("🚀 ROBLOX SCRIPT HUB запущен!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
